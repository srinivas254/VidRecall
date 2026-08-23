import os
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

my_hf_token = os.getenv("HUGGING_FACE_TOKEN")

#create a client to communicate with openAI model
client = Groq(api_key=my_api_key)

#embedding model & LLM model
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
LLM_MODEL = "openai/gpt-oss-20b"
SPARSE_RETRIEVAL_MODEL = "qdrant/bm25"
SPARSE_VECTOR_NAME = "chunk-text-bm25"

# Direct LLM vs RAG
DIRECT_LLM_THRESHOLD = 3000
SIMILARITY_THRESHOLD = 0.7071

# Chunking
CHUNK_SIZE = 350
CHUNK_OVERLAP = 50

# top k chunks Retrieval
TOP_K = 3

#reciprocal rank fusion constant
RRF_K = 60

my_qdrant_api_key = os.getenv("QDRANT_API_KEY")

my_qdrant_url = os.getenv("QDRANT_URL")

#create a vectorDB client
qdrantClient = QdrantClient(
    url = my_qdrant_url,
    api_key = my_qdrant_api_key)

#collection name
COLLECTION_NAME = "youtubeTranscript"

