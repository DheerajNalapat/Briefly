# Configuration for NewsAPI collector
# Get your free API key at: https://newsapi.org/register

from dotenv import load_dotenv
import os

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Example usage:
# from config import NEWSAPI_KEY
# collector = SimpleNewsAPICollector(NEWSAPI_KEY)
