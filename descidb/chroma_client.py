"""
ChromaDB vector database client for DeSciDB.

This module provides a VectorDatabaseManager class for managing ChromaDB collections
used to store document embeddings and perform vector similarity searches.
"""

import itertools
import os
from pathlib import Path

import chromadb


class VectorDatabaseManager:
    """
    Manages ChromaDB vector database collections for multiple embedding pipelines.

    This class handles the creation, initialization, and interaction with ChromaDB
    collections, which are used to store document embeddings.
    """

    def __init__(self, components: dict, db_path: str = None):
        """
        Initializes databases based on the Cartesian product of 'convert', 'chunker', and 'embedder'.

        Args:
            components: A dictionary with keys 'converter', 'chunker', and 'embedder',
                       each containing a list of values.
            db_path: Optional path to the database directory. If not provided,
                    will use the default 'database' directory in the descidb package.

        Raises:
            ValueError: If the components dictionary doesn't have the required keys.
        """
        if not all(key in components for key in ["converter", "chunker", "embedder"]):
            raise ValueError(
                "Components dictionary must have 'converter', 'chunker', and 'embedder' keys with lists of values."
            )

        self.db_names = [
            f"{c}_{ch}_{e}"
            for c, ch, e in itertools.product(
                components["converter"], components["chunker"], components["embedder"]
            )
        ]

        # Use the provided db_path or create a default path
        if db_path is None:
            # Get the directory where this module is located
            module_dir = Path(__file__).parent
            db_path = module_dir / "database"
        else:
            db_path = Path(db_path)

        # Ensure the database directory exists
        os.makedirs(db_path, exist_ok=True)

        self.db_client = chromadb.PersistentClient(path=str(db_path))
        self.initialize_databases()

    def initialize_databases(self):
        """
        Initializes or checks the existence of all databases (Cartesian product of convert, chunker, and embedder).
        """
        for db_name in self.db_names:
            self.db_client.get_or_create_collection(name=db_name)

    def insert_document(
        self, db_name: str, embedding: list, metadata: dict, doc_id: str
    ):
        """
        Inserts a document into the specified database.

        :param db_name: Name of the database where the document is to be inserted.
        :param embedding: The embedding of the document chunk to insert.
        :param metadata: Metadata associated with the document chunk.
        :param doc_id: Document ID to use for insertion.
        """
        if db_name not in self.db_names:
            raise ValueError(f"Database '{db_name}' does not exist.")

        # Insert document into the database
        collection = self.db_client.get_collection(name=db_name)
        try:
            collection.add(
                documents=[metadata["content_cid"]],
                embeddings=embedding,
                ids=[doc_id],
                metadatas=[metadata],
            )
        except Exception as e:
            print(f"Error inserting document into database '{db_name}': {e}")

    def print_all_metadata(self):
        """
        Retrieves and prints all metadata from every collection.
        """
        for db_name in self.db_names:
            collection = self.db_client.get_collection(name=db_name)
            # Retrieve all entries from the collection.
            # The structure of the returned results is assumed to contain a "metadatas" key.
            results = collection.get()
            metadatas = results.get("metadatas", [])
            print(f"\nMetadata for collection '{db_name}':")
            if not metadatas:
                print("  No metadata found.")
            else:
                for metadata in metadatas:
                    print(metadata)
