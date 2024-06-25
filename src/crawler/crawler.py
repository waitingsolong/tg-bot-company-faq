from abc import ABC, abstractmethod
from typing import List, Tuple
import asyncio
import logging
from firecrawl import FirecrawlApp
from openai_client.client import OpenAIClient


class FAQCrawler(ABC):
    def __init__(self, depth: int, openai_client):
        self.depth = depth
        self.openai_client = openai_client

    @abstractmethod
    async def crawl(self, url: str) -> List[Tuple[str, str]]:
        """
        Returns:
            [(url, content)], where 
            url - one-domain neighbour urls to 'url', 
            content - purified content from url
        """
        pass


class FirecrawlCrawler(FAQCrawler):
    parser_id_counter = 0

    def __init__(self, depth: int, openai_client: OpenAIClient, api_key: str):
        super().__init__(depth, openai_client)
        self.app = FirecrawlApp(api_key=api_key)

        FirecrawlCrawler.parser_id_counter += 1
        self.parser_id = FirecrawlCrawler.parser_id_counter
        
        
    async def crawl(self, url: str) -> List[Tuple[str, str]]:
        params = {
            'crawlerOptions': {
                'excludes': [],
                'includes': [],
                'limit': self.depth,
            },
            'pageOptions': {
                'onlyMainContent': True
            }
        }
        
        logging.info(f"Crawler {self.parser_id}: start crawling")
        try:
            crawl_results = self.app.crawl_url(url=url, params=params, wait_until_done=True)
        except Exception as e: 
            logging.error(f"Crawler {self.parser_id}: error crawling")
            logging.exception(e)
            return 
            
        res = []
        for cr in crawl_results:
            if cr['metadata']['pageStatusCode'] == 200:
                logging.info(f"Crawler {self.parser_id}: result added:\n{cr['metadata']['sourceURL']}")
                res.append((cr['metadata']['sourceURL'], cr['markdown']))
            else: 
                logging.error(f"Crawler {self.parser_id}: result error:\n{cr['metadata']['sourceURL']}\nStatus code:{cr['metadata']['pageStatusCode']}")
       
        return res
    

class HomemadeCrawler(FAQCrawler):
    parser_id_counter = 0

    def __init__(self, depth: int, openai_client):
        super().__init__(depth, openai_client)
        HomemadeCrawler.parser_id_counter += 1
        self.parser_id = HomemadeCrawler.parser_id_counter


    async def crawl(self, url: str) -> List[Tuple[str, str]]:
        neighbour_urls = await self.__get_neighbour_urls(url, self.depth)
        tasks = [self.__process_url(neighbour_url) for neighbour_url in neighbour_urls]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result]


    async def __process_url(self, url: str) -> Tuple[str, str]:
        dom_skeleton = await self.__get_dom_skeleton(url)
        cleaned_dom_skeleton = await self.__clean_dom_skeleton(dom_skeleton)
        cleaned_content = await self.__get_cleaned_content(cleaned_dom_skeleton)
        return (url, cleaned_content)


    async def __get_neighbour_urls(self, url: str, depth: int) -> List[str]:
        pass


    async def __get_dom_skeleton(self, url: str) -> str:
        pass


    async def __clean_dom_skeleton(self, dom_skeleton: str) -> str:
        pass


    async def __get_cleaned_content(self, cleaned_dom_skeleton: str) -> str:
        pass
