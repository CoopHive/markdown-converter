"""
Vector database query module for DeSciDB.

This module provides functions for querying ChromaDB collections with natural
language queries and retrieving relevant document chunks.
"""

import json
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv

from descidb.utils.logging_utils import get_logger
from descidb.core.embedder import embed, EmbederType

# Get module logger
logger = get_logger(__name__)

load_dotenv()


def query_collection(collection_name, user_query, db_path=None):
    """
    Query a ChromaDB collection with a natural language query.

    This function converts the user query to an embedding using the embedder module
    and performs a similarity search in the specified ChromaDB collection.

    If embedder_type is not specified, it will be extracted from the collection name
    (the part after the last underscore).

    Args:
        collection_name: Name of the ChromaDB collection to query
        user_query: Natural language query string
        db_path: Optional path to ChromaDB directory. If None, uses default path
        embedder_type: Type of embedder to use (openai, nvidia). If None, extracted from collection_name

    Returns:
        JSON string containing query results with metadata and similarity scores
    """
    try:
        parts = collection_name.split('_')
        if len(parts) > 1:
            embedder_type = parts[-1]
            logger.info(f"Using embedder type '{embedder_type}' derived from collection name")
        else:
            embedder_type = "openai"
            logger.info(f"Using default embedder type 'openai' as collection name has no underscore")

        # Use the provided db_path or create a default path
        if db_path is None:
            # Get the directory where this module is located and use its database subdirectory
            module_dir = Path(__file__).parent.parent
            db_path = module_dir / "database"
        else:
            db_path = Path(db_path)

        # Ensure the db_path exists
        os.makedirs(db_path, exist_ok=True)

        logger.info(
            f"Querying collection '{collection_name}' with: '{user_query[:50]}...'"
        )
        client = chromadb.PersistentClient(path=str(db_path))

        # Get collection
        collection = client.get_collection(name=f"{collection_name}")

        # Generate embedding using the embedder module with the determined embedder_type
        embedding = embed(embeder_type=embedder_type, input_text=user_query)

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
