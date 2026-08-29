import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set")