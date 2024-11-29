import os

from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModel

load_dotenv(override=True)


class Embedder:
    def __init__(self) -> None:
        """
        Initializes the Embedder with available embedding functions.

        :param openai_api_key: API key for OpenAI embeddings.
        :param functions: A list of embedding function names (e.g., 'openai_embed', 'nvidia_embed').
        """

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # # Conditionally initialize Nvidia model and tokenizer if 'nvidia_embed' is in the function list
        # if 'nvidia_embed' in self.functions:
        #     self.nvidia_model = AutoModel.from_pretrained(
        #         'nvidia/NV-Embed-v1', trust_remote_code=True)
        #     self.nvidia_tokenizer = AutoTokenizer.from_pretrained(
        #         'nvidia/NV-Embed-v1')

    def openai(self, text: str) -> list:
        """Embed text using the OpenAI embedding API. Returns a list."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small", input=[text]
        )
        embedding = response.data[0].embedding
        return embedding

    def nvidia(self, text: str) -> list:
        passage_prefix = ""
        paragraph_list = [text]
        model = AutoModel.from_pretrained("nvidia/NV-Embed-v1", trust_remote_code=True)
        max_length = 4096
        passage_embeddings = model.encode(
            paragraph_list, instruction=passage_prefix, max_length=max_length
        )
        return passage_embeddings.tolist()
