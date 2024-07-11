import os
import chromadb
import subprocess
import sys
import json
import openai
import requests


def create_database(databasename, version):
    db_path = os.path.join(os.path.dirname(__file__), 'database')
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(
        name=f"{databasename}v{version}")
    return collection


def chunk_document(document):
    paragraphs = document.split('\n\n')
    return paragraphs


def pargaraph_to_openai_input(paragraph, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        model=model, input=[paragraph], api_key="OPENAI_API_KEY")
    embedding = response['data'][0]['embedding']
    return embedding


def insert_document(collection, document, id, metadata):

    chunked_document = chunk_document(document)

    for i, paragraph in enumerate(chunked_document):
        embedded_paragraph = pargaraph_to_openai_input(paragraph)
        chunk_metadata = {**metadata, 'chunk_index': i}
        collection.add(
            documents=[embedded_paragraph],
            ids=[f"{id}_{i}"],
            metadatas=[chunk_metadata]
        )

    print(f"Document with id {id} added to the collection successfully.")


def print_all_documents(collection):
    documents = collection.get(include=["documents", "metadatas"])

    for doc_id, doc, meta in zip(documents['ids'], documents['documents'], documents['metadatas']):
        print(f"ID: {doc_id}")
        print(f"Document: {doc}")
        print(f"Metadata: {meta}")
        print("------")
