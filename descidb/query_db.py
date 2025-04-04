"""
Vector database query module for DeSciDB.

This module provides functions for querying ChromaDB collections with natural
language queries and retrieving relevant document chunks.
"""

import os
import json
from pathlib import Path
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from descidb.logging_utils import get_logger

# Get module logger
logger = get_logger(__name__)

load_dotenv()


def query_collection(collection_name, user_query, db_path=None):
    """
    Query a ChromaDB collection with a natural language query.

    This function converts the user query to an embedding using OpenAI's
    text-embedding model and performs a similarity search in the specified
    ChromaDB collection.

    Args:
        collection_name: Name of the ChromaDB collection to query
        user_query: Natural language query string
        db_path: Optional path to ChromaDB directory. If None, uses default path

    Returns:
        JSON string containing query results with metadata and similarity scores
    """
    try:
        openaiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OpenAI API key is not set in environment variables")
            return json.dumps({"error": "OpenAI API key not configured"})

        # Use the provided db_path or create a default path
        if db_path is None:
            # Get the directory where this module is located and use its database subdirectory
            module_dir = Path(__file__).parent
            db_path = module_dir / "database"
        else:
            db_path = Path(db_path)

        # Ensure the db_path exists
        os.makedirs(db_path, exist_ok=True)

        logger.info(
            f"Querying collection '{collection_name}' with: '{user_query[:50]}...'"
        )
        client = chromadb.PersistentClient(path=str(db_path))
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key="", model_name="text-embedding-3-small"
        )
        collection = client.get_collection(
            name=f"{collection_name}", embedding_function=openai_ef
        )

        model_name = "text-embedding-3-small"
        response = openaiClient.embeddings.create(model=model_name, input=[user_query])
        embedding = response.data[0].embedding
        values = collection.query(
            query_embeddings=[embedding],
            n_results=4,
            include=["metadatas", "documents", "distances"],
        )

        result = {"query": user_query, "results": []}

        if values["ids"] and len(values["ids"][0]) > 0:
            for i in range(len(values["ids"][0])):
                result["results"].append(
                    {
                        "document": values["documents"][0][i]
                        if i < len(values["documents"][0])
                        else "",
                        "metadata": values["metadatas"][0][i]
                        if i < len(values["metadatas"][0])
                        else {},
                        "distance": values["distances"][0][i]
                        if i < len(values["distances"][0])
                        else 0,
                    }
                )

            logger.info(f"Found {len(result['results'])} results for query")
            return json.dumps(result)
        else:
            logger.warning(f"No results found for query: '{user_query[:50]}...'")
            return json.dumps({"query": user_query, "results": []})

    except Exception as e:
        logger.error(f"Error querying collection: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    print(
        query_collection(
            "openai_fixed_length_openai",
            "What are the challenges in assessing gene editing outcomes in human embryos?",
        )
    )
