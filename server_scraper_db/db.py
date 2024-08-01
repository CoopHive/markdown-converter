import requests
import os
import chromadb
import subprocess
import sys
import json
from openai import OpenAI
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
import re
import chromadb.utils.embedding_functions as embedding_functions


class DocumentDatabase:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=self.openai_api_key)
        db_path = os.path.join(os.path.dirname(__file__), 'database')
        self.db_client = chromadb.PersistentClient(path=db_path)
        self.nvidia_model = None
        self.nvidia_tokenizer = None

    def create_database(self, databasename):
        return self.create_openai_db(databasename), self.create_nvidia_db(databasename)

    def chunk_document(self, document, strategy='paragraph'):
        print(f"Chunking strategy received: {strategy}")  # Debugging line
        if strategy == 'paragraph':
            chunks = document.split('\n\n')
        elif strategy == 'sentence':
            chunks = re.split(
                r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', document)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # Filter out empty or whitespace-only chunks
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
            api_key="sk-proj-OqH5ok75imwtsbJKZrH7T3BlbkFJK9fL3mmdg5e4uryrf9vd",
            model_name="text-embedding-3-small"
        )
        return self.db_client.get_or_create_collection(name=f"{databasename}_openai", embedding_function=openai_ef)

    def create_nvidia_db(self, databasename):
        nvidia_ef = embedding_functions.HuggingFaceEmbeddingFunction(
            api_key="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",
            model_name="nvidia/NV-Embed-v1"
        )
        return self.db_client.get_or_create_collection(name=f"{databasename}_openai", embedding_function=nvidia_ef)

    def paragraph_to_nvidia_input(self, paragraph, model_name='nvidia/NV-Embed-v1'):
        if self.nvidia_model is None or self.nvidia_tokenizer is None:
            self.nvidia_model = AutoModel.from_pretrained(
                model_name, trust_remote_code=True)
            self.nvidia_tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True)

        inputs = self.nvidia_tokenizer(
            paragraph, return_tensors="pt", padding=True, truncation=True)
        outputs = self.nvidia_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        normalized_embeddings = F.normalize(embeddings, p=2, dim=1)
        return normalized_embeddings[0].detach().numpy()

    def insert_document(self, document, collection, doc_id, metadata, chunk_strategy='paragraph', embed_strategy='openai'):
        # Split the document into chunks based on the provided strategy
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
            # print(f"Chunk metadata: {chunk_metadata}")
            # print(doc_id)
            # print("-------------------------------------------------")
            # print("-------------------------------------------------")
            # print("-------------------------------------------------")

            collection.add(
                documents=[chunk],
                embeddings=[embedded_chunk],
                ids=[f"{doc_id}_{i}"],
                metadatas=[chunk_metadata]
            )

        print(
            f"Document with id {doc_id} added to the collection successfully.")

    def print_all_documents(self, collection):

        documents = collection.get(include=["documents", "metadatas"])

        for doc_id, doc, meta in zip(documents['ids'], documents['documents'], documents['metadatas']):
            print(f"ID: {doc}")
            # print(f"Metadata: {meta}")
            print("-------------------------------------------------")
            print("-------------------------------------------------")
            print("-------------------------------------------------")
