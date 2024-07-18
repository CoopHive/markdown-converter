import requests
import os
import chromadb
import subprocess
import sys
import json
from openai import OpenAI


class DocumentDatabase:
    def __init__(self, openai_api_key, db_host='localhost', db_port=8000):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=self.openai_api_key)
        self.db_client = chromadb.HttpClient(host=db_host, port=db_port)

    def create_database(self, databasename, version):
        self.collection = self.db_client.get_or_create_collection(
            name=f"{databasename}v{version}")
        return self.collection

    @staticmethod
    def chunk_document(document):
        paragraphs = document.split('\n\n')
        return paragraphs

    def paragraph_to_openai_input(self, paragraph, model="text-embedding-ada-002"):
        response = self.client.embeddings.create(
            model=model, input=[paragraph])
        embedding = response.data[0].embedding
        return embedding

    def insert_document(self, document, doc_id, metadata):
        chunked_document = self.chunk_document(document)

        for i, paragraph in enumerate(chunked_document):
            embedded_paragraph = self.paragraph_to_openai_input(paragraph)
            chunk_metadata = {**metadata, 'chunk_index': i}
            self.collection.add(
                documents=[embedded_paragraph],
                ids=[f"{doc_id}_{i}"],
                metadatas=[chunk_metadata]
            )

        print(
            f"Document with id {doc_id} added to the collection successfully.")

    def print_all_documents(self):
        documents = self.collection.get(include=["documents", "metadatas"])

        for doc_id, doc, meta in zip(documents['ids'], documents['documents'], documents['metadatas']):
            print(f"ID: {doc_id}")
            print(f"Document: {doc}")
            print(f"Metadata: {meta}")
            print("------")
