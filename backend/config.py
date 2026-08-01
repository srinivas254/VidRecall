import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

my_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=my_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "openai/gpt-oss-20b:free"
