import httpx
import logging


async def validate_url(url: str) -> bool:
    if not url:
        logging.info("No url provided to validate url")
        return False
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return True
            else:
                logging.error(f"URL validation failed with status code: {response.status}\n{url}")
                return False
    except Exception as e:
        logging.error(f"{url}\nException occurred during URL validation: {e}")
        return False
