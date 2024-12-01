import itertools
import os

import chromadb


class VectorDatabaseManager:
    def __init__(self, components: dict):
        """
        Initializes databases based on the Cartesian product of 'convert', 'chunker', and 'embedder'.

        :param components: A dictionary with keys 'convert', 'chunker', and 'embedder', each containing a list of values.
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

        self.db_client = chromadb.PersistentClient(
            path=os.path.join(os.path.dirname(__file__), "database")
        )

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
        collection.add(
            documents=[metadata["title"]],
            embeddings=[embedding],
            ids=[doc_id],
            metadatas=[metadata],
        )
