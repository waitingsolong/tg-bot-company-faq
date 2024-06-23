import os
from dotenv import load_dotenv


load_dotenv()

 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = bool(os.getenv("DEBUG"))

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT") 
