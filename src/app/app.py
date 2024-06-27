import copy
from openai_client.client import OpenAIClient 
from crawler.logic import run_crawlers, init_crawlers
import logging 
from typing import Optional
from utils.clean_markdown_contents import clean_markdown_contents
from config import FIRECRAWL_API_KEY


class App():
    def __init__(self, openai_client: OpenAIClient):
        self.__openai_client = openai_client
        self.__able_to_faq = False
        
        firecrawl_api_keys = [FIRECRAWL_API_KEY]
        self.__crawlers = init_crawlers(openai_client, firecrawl_api_keys)
    
    
    def get_openai_client(self):
        return self.__openai_client
    
        
    async def gather_info(self, url: str) -> bool:
        """
        Run crawlers, add results to vector stores
        
        Raises:
            e: fail run crawlers 
            e: fail adding to vector store
        """
        logging.info("Gathering company info started")
            
        ##########
        # CRAWLING
        try: 
            logging.info("Crawlers run started")
            results = await run_crawlers(self.__crawlers, url)
            logging.info("Crawlers run completed")
        except Exception as e: 
            logging.error("Crawlers run failed with error")
            raise e
        
        crawl_result = None
        succ_crawls = 0
        err_crawls = 0 
        logging.info("Checking for aggregated crawl results")
        for i, result in enumerate(results):
            logging.info(f"Crawler {self.__crawlers[i].parser_id}")
            if result["exception"]:
                err_crawls += 1
                logging.info(f"Error: {result['exception']}")
            elif result['crawl_result']:
                succ_crawls += 1
                crawl_result = result['crawl_result']
                logging.info(f"Success! Result's urls:\n{[url_content[0] for url_content in result['crawl_result']]}")
            else: 
                logging.error("Undefined crawl result")
        
        logging.info(f"From {len(results)} crawlers: {succ_crawls} succeed, {err_crawls} failed")
        
        if not crawl_result: 
            logging.error("No results got from crawlers")
            return False 
        
        ###############
        # HAND CLEANING        
        documents_before = [url_content[1] for url_content in crawl_result]
        docs_size_before = sum([len(d) for d in documents_before])
        
        logging.info(f"Content before hand cleanup:\n{documents_before}")
        try:
            logging.info("Hand cleaning started") 
            documents = clean_markdown_contents(documents_before)
            logging.info("Hand cleaning completed")    
        except Exception as e: 
            logging.error("Hand cleaning failed with error")
            raise e 
        logging.info(f"Total size before hand: {docs_size_before}, after hand: {sum([len(d) for d in documents])}")
        logging.info(f"Content after hand cleanup:\n{documents}")
        
        ##################
        # CHATGPT CLEANING
        clean_task="""Context: I develop FAQ company bot for users ask questions about company.
        I give you company's parsed site content.
        You need to clear the site content from unnecessary information, such as
        site footer, cookie policy, fields with errors, login fields, urls, etc. 
        """
        documents_before = copy.deepcopy(documents)
        docs_size_before = sum([len(d) for d in documents_before])
        documents = []
        try:
            logging.info("GPT cleaning started")
            for document in documents_before: 
                doc_size_before = len(document)
                logging.info(f"Document before gpt cleaning:\n{document}")
                new_document = await self.__openai_client.query(prompt=document, task=clean_task)
                documents.append(new_document)
                logging.info(f"Size before: {doc_size_before}, size after: {len(new_document)}")
                logging.info(f"Document after gpt cleaning:\n{new_document}")
            logging.info("GPT cleaning completed")    
        except Exception as e: 
            logging.error("GPT cleaning failed with error")
            raise e 
        logging.info(f"Total size before GPT: {docs_size_before}, total size after GPT: {sum([len(d) for d in documents])}")
        
        ##############
        # VECTOR STORE 
        try:
            logging.info("Adding results to vector store started") 
            await self.__openai_client.add_to_vector_store(documents)
            logging.info("Adding results to vector store completed")    
        except Exception as e: 
            logging.info("Adding results to vector store failed with error")
            raise e 
        
        self.__able_to_faq = True
        logging.info("Gathering company info ended")
        return True
        
    
    async def faq(self, question: str) -> Optional[str]: 
        if not self.__able_to_faq:
            logging.info("Not able to faq")
            return None
        
        try: 
            return await self.__openai_client.rag(question)
        except Exception as e: 
            logging.error("Error FAQing")
            logging.exception(e)
            return None 
        
    