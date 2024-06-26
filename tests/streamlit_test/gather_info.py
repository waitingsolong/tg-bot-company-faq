import src.logs
import streamlit as st
from src.openai_client.client import OpenAIClient
from src.crawler.logic import run_crawlers, init_crawlers
import logging
from src.utils.clean_markdown_contents import clean_markdown_contents
from src.config import FIRECRAWL_API_KEY
from typing import Optional
import asyncio
import streamlit as st
import copy

from src.utils.diff import generate_diff_html 

openai_client = None
crawlers = None
able_to_faq = False

def initialize():
    global openai_client, crawlers
    openai_client = OpenAIClient()
    firecrawl_api_keys = [FIRECRAWL_API_KEY]
    crawlers = init_crawlers(openai_client, firecrawl_api_keys)

@st.cache_resource
async def faq_streamlit(question: str) -> Optional[str]:
    global able_to_faq
    if not able_to_faq:
        logging.info("No able to faq")
        return None
    
    try:
        response = await openai_client.rag(question)
        if not response: 
            logging.info("No response came from rag")
        return response
    except Exception as e:
        logging.error("Error FAQing")
        logging.exception(e)
        raise e

@st.cache_resource
async def gather_info_streamlit(url: str):
    ##########
    # CRAWLERS
    global able_to_faq, crawlers
    st.write("## Gathering company info started")
    try:
        st.write("### Crawlers run started")
        results = await run_crawlers(crawlers, url)
        st.write("### Crawlers run completed")
    except Exception as e:
        st.error("### Crawlers run failed with error")
        st.session_state.gather_info_status = "failed"
        raise e

    crawl_result = None
    succ_crawls = 0
    err_crawls = 0
    st.write("## Checking for aggregated crawl results")
    for i, result in enumerate(results):
        st.write(f"#### Crawler {crawlers[i].parser_id}")
        if result["exception"]:
            err_crawls += 1
            st.error(f"Error: {result['exception']}")
        else:
            succ_crawls += 1
            crawl_result = result['crawl_result']
            st.write(f"Success! Result's urls:\n{[url_cont[0] for url_cont in result['crawl_result']]}")
    
    st.write(f"### From {len(results)} crawlers: {succ_crawls} succeed, {err_crawls} failed")
    
    if not crawl_result:
        st.error("No results got from crawlers")
        st.session_state.gather_info_status = "failed"
        return False
    
    ############
    # HAND CLEAN
    N_docs = len(crawl_result)
    docs_urls = [url_content[0] for url_content in crawl_result] 
    documents_before = [url_content[1] for url_content in crawl_result]
    docs_size_before = sum([len(d) for d in documents_before])
    
    try:
        st.write("### Hand cleaning started")
        documents = clean_markdown_contents(documents_before)
        st.write("### Hand cleaning completed")
    except Exception as e:
        st.error("Hand cleaning failed with error")
        st.session_state.gather_info_status = "failed"
        raise e
    
    st.write(f"### Total size before hand cleanup: {docs_size_before}")
    st.write(f"### Total size after hand cleanup: {sum([len(d) for d in documents])}")
    
    
    with st.expander("Contents before/after hand cleanup:"):
        try:
            diff_html = generate_diff_html(documents_before, documents)
            st.markdown(diff_html, unsafe_allow_html=True)
        except Exception as e: 
            logging.error("Error writing diffs")
            logging.exception(e)

            col1, col2 = st.columns(2)
            col1.subheader("Before hand cleanup")
            col2.subheader("After hand cleanup")
            col1.write(documents_before)
            col2.write(documents)
    
    ###########
    # GPT CLEAN
    clean_task = """Context: I develop FAQ company bot for users ask questions about company.
    I give you company's parsed site content.
    You need to clear the site content from unnecessary information, compress it to the minimum necessary information.
    Delete site footer, cookie policy, fields with errors, login fields, urls, privacy policy, info about site, etc.
    """
    
    documents_before = copy.deepcopy(documents)
    docs_size_before = sum([len(d) for d in documents])
    documents = []

    error_diffs = False
     
    try:
        st.write("### GPT cleaning started")
        for i, document in enumerate(documents_before):
            new_document = await openai_client.query(prompt=document, task=clean_task)
            documents.append(new_document)
            
            with st.expander(f"{docs_urls[i]}"):
                try:
                    diff_html = generate_diff_html(document, new_document)
                    st.markdown(diff_html, unsafe_allow_html=True)
                except Exception as e: 
                    logging.error("Error writing diffs")
                    if not error_diffs:
                        error_diffs = True
                        logging.exception(e)
                    
                    st.write(f"{docs_urls[i]}")
                    col1, col2 = st.columns(2)
                    col1.subheader("Before GPT cleanup")
                    col2.subheader("After GPT cleanup")
                    col1.write(f"[size={len(document)}]\n\n{document}")
                    col2.write(f"[size={len(new_document)}]\n\n{new_document}")
            
        st.write("### GPT cleaning completed")
    except Exception as e:
        st.error("### GPT cleaning failed with error")
        st.session_state.gather_info_status = "failed"
        raise e
    
    st.write(f"### Total size before GPT cleanup: {docs_size_before}")
    st.write(f"### Total size after GPT cleanup: {sum([len(d) for d in documents])}")
    
    ##############
    # VECTOR STORE
    try:
        st.write("## Adding results to vector store started")
        await openai_client.add_to_vector_store(documents)
        st.write("## Adding results to vector store completed")
    except Exception as e:
        st.error("Adding results to vector store failed with error")
        st.session_state.gather_info_status = "failed"
        raise e
    
    ############
    # TOKEN USAGE
    input_tokens, output_tokens = openai_client.pop_session_delta_inout_tokens()
    cost = openai_client.calculate_inout_cost(input_tokens, output_tokens)
    st.write(f"### Input tokens: {input_tokens}, Output tokens: {output_tokens}")
    st.write(f"### Cost of this session: ${cost:.6f}")
    
    logging.info("Now bot is able to faq you")
    able_to_faq = True
    st.session_state.gather_info_status = "completed"
    st.write("# Gathering company info ended")
    return True
