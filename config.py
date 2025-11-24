import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4-turbo"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "data/memory.json"
