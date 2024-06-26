from crawler.crawler import FirecrawlCrawler, FAQCrawler
from openai_client.client import OpenAIClient
import asyncio


def init_crawlers(openai_client: OpenAIClient, firecrawl_api_keys: list[str], depth=5):
    crawlers = [FirecrawlCrawler(depth, openai_client, api_key) for api_key in firecrawl_api_keys]
    return crawlers


async def run_crawler(crawler: FAQCrawler, url) -> dict:
    try:
        result = await crawler.crawl(url)
        return {"crawl_result": result, "exception": None}
    except Exception as e:
        return {"crawl_result": None, "exception": e}


async def run_crawlers(crawlers: list[FAQCrawler], url: str) -> list[dict]:
    """
    Returns:
        [{"crawl_result":, "exception":}]
    """
    tasks = [run_crawler(cr, url) for cr in crawlers]
    results = await asyncio.gather(*tasks)
    return results
    