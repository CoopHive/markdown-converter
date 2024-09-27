import os
import chromadb
import json
from openai import OpenAI
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
import re
import chromadb.utils.embedding_functions as embedding_functions
from postgres import PostgresDBManager
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


class DocumentDatabase:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=self.openai_api_key)
        db_path = os.path.join(os.path.dirname(__file__), 'database')
        self.db_client = chromadb.PersistentClient(path=db_path)
        self.postgres_db_manager = PostgresDBManager(
            host="localhost", port=5432, user="vardhanshorewala", password="password")

    def load_contract_abi(self, abi_path):
        with open(abi_path, 'r') as abi_file:
            return json.load(abi_file)

    def create_database(self, databasename):
        return self.create_nvidia_db(databasename), self.create_openai_db(databasename)

    def chunk_document(self, document, strategy='paragraph'):
        if strategy == 'paragraph':
            chunks = document.split('\n\n')
        elif strategy == 'sentence':
            chunks = [document[i:i + 400]
                      for i in range(0, len(document), 400)]
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        chunks = [str(chunk) for chunk in chunks if chunk]
        return chunks

    def paragraph_to_openai_input(self, paragraph):
        response = self.client.embeddings.create(
            model="text-embedding-3-small", input=[paragraph])
        embedding = response.data[0].embedding
        return embedding

    def create_openai_db(self, databasename):
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key="",
            model_name="text-embedding-3-small"
        )
        return self.db_client.get_or_create_collection(name=f"{databasename}_openai", embedding_function=openai_ef)

    def create_nvidia_db(self, databasename):
        nvidia_ef = embedding_functions.HuggingFaceEmbeddingFunction(
            api_key="",
            model_name="nvidia/NV-Embed-v1"
        )
        return self.db_client.get_or_create_collection(name=f"{databasename}_nvidia", embedding_function=nvidia_ef)

    def paragraph_to_nvidia_input(self, paragraph):
        passage_prefix = ""
        paragraph_list = [paragraph]
        model = AutoModel.from_pretrained(
            'nvidia/NV-Embed-v1', trust_remote_code=True)
        max_length = 4096
        passage_embeddings = model.encode(
            paragraph_list, instruction=passage_prefix, max_length=max_length)
        return passage_embeddings.tolist()

    def insert_document(self, document, collection, doc_id, metadata, chunk_strategy='paragraph', embed_strategy='openai', postgresdb='papers', author="invalid"):
        chunked_document = self.chunk_document(
            document=document, strategy=chunk_strategy)

        for i, chunk in enumerate(chunked_document):
            if embed_strategy == 'openai':
                embedded_chunk = self.paragraph_to_openai_input(chunk)
            elif embed_strategy == 'nvidia':
                embedded_chunk = self.paragraph_to_nvidia_input(chunk)
            else:
                raise ValueError(
                    f"Unknown embedding strategy: {embed_strategy}")

            chunk_metadata = {key: (value if value is not None else 'N/A')
                              for key, value in metadata.items()}
            chunk_metadata['chunk_index'] = i

            self.postgres_db_manager.insert_data(
                db_name=postgresdb,
                data=[(author, metadata['title'], chunk,
                       embedded_chunk, json.dumps(chunk_metadata), False)]  # False for 'rewarded' field
            )

            collection.add(
                documents=[chunk],
                embeddings=embedded_chunk,
                ids=[f"{doc_id}_{i}"],
                metadatas=[chunk_metadata]
            )
