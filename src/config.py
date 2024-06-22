import os
from dotenv import load_dotenv


load_dotenv()


SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = bool(os.getenv("DEBUG"))
