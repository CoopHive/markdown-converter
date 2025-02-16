import os
import json
from functools import wraps
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def query_collection(collection_name, user_query):
    openaiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    db_path = "/Users/vardhanshorewala/Desktop/coophive/markdown-converter/descidb/database"
    client = chromadb.PersistentClient(path=db_path)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key="", model_name="text-embedding-3-small"
    )
    collection = client.get_collection(
        name=f"{collection_name}", embedding_function=openai_ef
    )

    model_name = "text-embedding-3-small"
    response = openaiClient.embeddings.create(
        model=model_name, input=[user_query])
    embedding = response.data[0].embedding
    values = collection.query(
        query_embeddings=[embedding],
        n_results=5,
        include=["metadatas", "documents", "distances"]
    )

    results = []
    for i, metadata in enumerate(values["metadatas"][0]):
        results.append({
            "distance": values["distances"][0][i],
            "content": metadata["content"],
            "content_cid": metadata["content_cid"],
            "embedding_cid": metadata["embedding_cid"],
            "root_cid": metadata["root_cid"]
        })

    output = {
        "query": user_query,
        "results": results
    }

    return json.dumps(output, indent=4)
