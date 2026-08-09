from transformers import AutoTokenizer,AutoModel
from config import EMBEDDING_MODEL,my_hf_token

tokenizer = AutoTokenizer.from_pretrained(
    EMBEDDING_MODEL,
    token=my_hf_token
)

model = AutoModel.from_pretrained(
    EMBEDDING_MODEL,
    token=my_hf_token
)