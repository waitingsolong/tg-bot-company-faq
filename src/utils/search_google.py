import serpapi
from .logged_step import logged_step
from src.config import SERPAPI_API_KEY


client = serpapi.Client(api_key=SERPAPI_API_KEY)


@logged_step("Searching")
def search_google(q: str) -> list:
    """
    Returns:
        list: urls
    """
    serpapi_results = client.search(
        q="coffee",
        engine="google",
        location="Austin, Texas",
        hl="en",
        gl="us",
    )
    return get_links(serpapi_results)

    
def get_links(serpapi_results) -> list:
    return [x['link'] for x in serpapi_results.data['organic_results']] 
