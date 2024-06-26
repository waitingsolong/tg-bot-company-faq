import os
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv()
 
 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = bool(strtobool(os.getenv("DEBUG")))
STREAMLIT_MODE = bool(strtobool(os.getenv("STREAMLIT_MODE")))
AUTH_KEY = os.getenv("AUTH_KEY")

REDIS = bool(strtobool(os.getenv("REDIS")))
REDIS_BY_PRIVATE = bool(strtobool(os.getenv("REDIS_BY_PRIVATE")))
REDIS_PRIVATE_URL = os.getenv("REDIS_PRIVATE_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT") 

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY") 
