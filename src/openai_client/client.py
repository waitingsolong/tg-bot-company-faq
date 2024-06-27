import logs
from pathlib import Path
import uuid
import aiofiles
import logging
from langchain_openai import ChatOpenAI
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_community.callbacks.manager import get_openai_callback
from utils.logged_token_usage import log_token_usage
from utils.logged_step import logged_step
from langchain.schema import Document
from openai import AsyncOpenAI
from config import AUDIO_DIR, DEBUG

if not DEBUG:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


class OpenAIClient:
    input_1M_token_price = {
        "gpt-3.5-turbo-1106": 1.0,
    }
    
    output_1M_token_price = {
        "gpt-3.5-turbo-1106": 2.0,
    }
    
    vector_store_cost_per_gb_per_day = 0.0
    whisperer_cost_per_sec = 0.0001
    tts_cost_per_1k_input_chars = 0.015

    def __init__(self, model_name: str = "gpt-3.5-turbo-1106"):
        if model_name not in set(OpenAIClient.input_1M_token_price.keys()).union(OpenAIClient.output_1M_token_price.keys()):
            logging.critical(f"Input/output price for model {model_name} is not specified. Please, select allowed model")
            raise Exception()
                
        self.__model_name = model_name
        self.__llm = ChatOpenAI(model_name=model_name)
        self.__native_openai_client = AsyncOpenAI()

        self.__input_tokens = 0
        self.__output_tokens = 0
        self.__delta_input_tokens = 0
        self.__delta_output_tokens = 0
        self.__delta_session_input_tokens = 0
        self.__delta_session_output_tokens = 0
        self.__vector_store_size_gb = 0.0
        self.__whisperer_cost = 0.0
        self.__tts_cost = 0.0

        # query chain 
        query_prompt_template = ChatPromptTemplate.from_template("{task}\n\nPrompt: {prompt}")
        self.__query_chain = query_prompt_template | self.__llm | StrOutputParser() 

        # rag chain
        embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
        self.__vector_store = None
        try:
            self.__vector_store = Chroma(embedding_function=embeddings)
        except Exception as e:
            logging.error(f"Error initializing Chroma: {e}")
            logging.critical("No vector store initialized")
            
            
        retriever = self.__vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})
        rag_prompt_template = hub.pull("rlm/rag-prompt")
        setup_and_retrieval = RunnableParallel(
            {"context": retriever | self.__format_docs, "question": RunnablePassthrough()}
        )
        self.__rag_chain = setup_and_retrieval | rag_prompt_template | self.__llm | StrOutputParser()  


    @logged_step("OpenAIClient destructor")
    def __del__(self):
        try:
            logging.info("Clearing vector store")
            self.clear_vector_store()
        except Exception as e:
            pass
        
        cost = self.calculate_cost()
        logging.info(f"Total cost of using ChatGPT: ${cost:.6f}")
    

    @log_token_usage("Query execution")
    async def query(self, task: str, prompt: str):
        """
        Raises:
            e: whatever
        """
        chain_input = {"task": task, "prompt": prompt}
        
        with get_openai_callback() as cb:
            res = await self.__query_chain.ainvoke(chain_input)
            self.__delta_input_tokens += cb.prompt_tokens
            self.__delta_output_tokens += cb.completion_tokens
    
        return res

    
    async def whisperer(self, mp3_file_path: str) -> Optional[str]:
        try:
            with open(mp3_file_path, "rb") as audio_file:
                translation = await self.__native_openai_client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
        except Exception as e:
            logging.error("Whisperer: Error:")
            logging.exception(e)
            return None

        duration_sec = int(Path(mp3_file_path).stat().st_size / 16000)  # Approximating duration from file size (16kbps)
        cost = duration_sec * self.whisperer_cost_per_sec
        self.__whisperer_cost += cost
        logging.info(f"Whisperer: User said:\n{translation}\n\nCost: ${cost:.6f} (${self.__whisperer_cost:.6f} total)")
            
        return translation

    async def tts(self, text: str) -> Optional[str]:
        mp3_file_path = AUDIO_DIR / f"{uuid.uuid4().hex}.mp3"
        
        try:
            async with self.__native_openai_client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="onyx",
                input=text
            ) as response:
                async with aiofiles.open(mp3_file_path, 'wb') as f:
                    async for chunk in response.iter_bytes():
                        await f.write(chunk)
        except Exception as e:
            logging.error("TTS: Error:")
            logging.exception(e)
            return None 
        
        if mp3_file_path.exists() and mp3_file_path.stat().st_size > 0:
            cost = len(text) / 1000 * 0.015
            self.__tts_cost += cost
            logging.info(f"TTS: Cost: ${cost:.6f} (${self.__tts_cost:.6f} total)")
            return mp3_file_path
        else:
            return None


    def calculate_cost(self) -> float:
        vector_store_cost = 0
        if self.__vector_store_size_gb > 1:
            vector_store_cost = (self.__vector_store_size_gb - 1) * self.vector_store_cost_per_gb_per_day
            
        return self.calculate_inout_cost(self.__input_tokens, self.__output_tokens) + \
            vector_store_cost + self.__whisperer_cost + self.__tts_cost
            
            
    def calculate_inout_cost(self, inp_tokens, out_tokens):
        return (inp_tokens / 1_000_000) * self.input_1M_token_price[self.__model_name] + \
            (out_tokens / 1_000_000) * self.output_1M_token_price[self.__model_name]

    
    def pop_session_delta_inout_tokens(self):
        in_out = (self.__delta_session_input_tokens, 
                  self.__delta_session_output_tokens)
        self.__delta_session_input_tokens = 0
        self.__delta_session_output_tokens = 0
        return in_out
        
                
    async def add_to_vector_store(self, documents: List[str]):
        chunk_size = 1_000
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
        doc_objects = [Document(page_content=doc) for doc in documents]
        docs = text_splitter.split_documents(doc_objects)
        await self.__vector_store.aadd_documents(docs)
        self.__vector_store_size_gb += self.__calculate_chunks_size_gb(docs, chunk_size)


    def __calculate_chunks_size_gb(self, chunks, chunk_size_in_bytes) -> float:
        return len(chunks) / chunk_size_in_bytes / 1000.0
    
    
    def __format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    
    @log_token_usage("Rag execution")
    async def rag(self, question: str) -> str:
        """
        Raises:
            e: whatever
        """        
        with get_openai_callback() as cb:
            ans = await self.__rag_chain.ainvoke(question)
            self.__delta_input_tokens += cb.prompt_tokens
            self.__delta_output_tokens += cb.completion_tokens
            return ans


    def clear_vector_store(self):
        if not self.__vector_store: 
            return
        
        self.__vector_store.delete_collection()
        