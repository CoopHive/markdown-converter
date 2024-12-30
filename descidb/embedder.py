import os
from typing import List, Literal


from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModel
from descidb.utils import download_from_url

load_dotenv(override=True)

EmbederType = Literal["openai", "nvidia"]


def embed_from_url(embeder_type: EmbederType, input_url: str) -> List[str]:
    """Embed based on the specified embedding type."""
    donwload_path = download_from_url(url=input_url)

    with open(donwload_path, "r") as file:
        input_text = file.read()

    return embed(embeder_type=embeder_type, input_text=input_text)


def embed(embeder_type: EmbederType, input_text: str) -> List[str]:
    """Chunk based on the specified chunking type."""

    chunking_methods = {"openai": openai, "nvidia": nvidia}

    return chunking_methods[embeder_type](text=input_text)


def openai(text: str) -> list:
    """Embed text using the OpenAI embedding API. Returns a list."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small", input=[text]
    )
    embedding = response.data[0].embedding
    return embedding


def nvidia(text: str) -> list:
    pass

# class Embedder:
#     def __init__(self) -> None:
#         """
#         Initializes the Embedder with available embedding functions.

#         :param openai_api_key: API key for OpenAI embeddings.
#         :param functions: A list of embedding function names (e.g., 'openai_embed', 'nvidia_embed').
#         """

#         self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#         # # Conditionally initialize Nvidia model and tokenizer if 'nvidia_embed' is in the function list
#         # if 'nvidia_embed' in self.functions:
#         #     self.nvidia_model = AutoModel.from_pretrained(
#         #         'nvidia/NV-Embed-v1', trust_remote_code=True)
#         #     self.nvidia_tokenizer = AutoTokenizer.from_pretrained(
#         #         'nvidia/NV-Embed-v1')

#     def openai(self, text: str) -> list:
#         """Embed text using the OpenAI embedding API. Returns a list."""
#         response = self.client.embeddings.create(
#             model="text-embedding-3-small", input=[text]
#         )
#         embedding = response.data[0].embedding
#         return embedding

#     def nvidia(self, text: str) -> list:
#         passage_prefix = ""
#         paragraph_list = [text]
#         model = AutoModel.from_pretrained("nvidia/NV-Embed-v1", trust_remote_code=True)
#         max_length = 4096
#         passage_embeddings = model.encode(
#             paragraph_list, instruction=passage_prefix, max_length=max_length
#         )
#         return passage_embeddings.tolist()
