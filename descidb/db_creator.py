"""
Database creation module for DeSciDB.

This module provides functionality to create and populate vector databases
by retrieving data from IPFS and processing graph relationships.
"""

import logging
import requests
import json
import os
from pathlib import Path
from descidb.graph_db import IPFSNeo4jGraph
from descidb.chroma_client import VectorDatabaseManager
from descidb.logging_utils import get_logger
import dotenv

dotenv.load_dotenv()

# Get module logger
logger = get_logger(__name__)


class DatabaseCreator:
    """
    Creates and populates vector databases from graph relationships.

    This class retrieves embeddings and content from IPFS based on graph
    relationships and inserts them into ChromaDB collections.
    """

    def __init__(self, graph, vector_db_manager):
        """
        Initialize the DatabaseCreator.

        Args:
            graph: IPFSNeo4jGraph instance for graph database operations
            vector_db_manager: VectorDatabaseManager instance for vector database operations
        """
        self.graph = graph
        self.vector_db_manager = vector_db_manager
        self.logger = get_logger(__name__ + '.DatabaseCreator')

    def query_lighthouse_for_embedding(self, cid):
        """
        Query Lighthouse IPFS gateway for an embedding vector.

        Args:
            cid: IPFS CID of the embedding

        Returns:
            List representation of the embedding vector or None if retrieval fails
        """
        url = f"https://gateway.lighthouse.storage/ipfs/{cid}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            embedding_vector = json.loads(response.text)
            return embedding_vector
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to retrieve embedding for CID {cid}: {e}")
            return None

    def query_ipfs_content(self, cid):
        url = f"https://gateway.lighthouse.storage/ipfs/{cid}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            return content
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"Failed to retrieve IPFS content for CID {cid}: {e}")
            return None

    def process_paths(self, start_cid, path, db_name):
        paths = self.graph.recreate_path(start_cid, path)
        self.logger.info(f"Found {len(paths)} paths for CID {start_cid}")
        if not paths:
            self.logger.error(f"No valid paths found for CID {start_cid}")
            return

        for path_nodes in paths:
            if len(path_nodes) < 2:
                self.logger.error(f"Path {path_nodes} is too short.")
                continue

            content_cid = path_nodes[-2]
            embedding_cid = path_nodes[-1]

            embedding_vector = self.query_lighthouse_for_embedding(
                embedding_cid)
            if embedding_vector is None:
                self.logger.error(
                    f"Skipping path {path_nodes} due to failed embedding retrieval.")
                continue

            content = self.query_ipfs_content(content_cid)
            if content is None:
                self.logger.error(
                    f"Skipping path {path_nodes} due to failed IPFS content retrieval.")
                continue

            metadata = {
                "content_cid": content_cid,
                "root_cid": start_cid,
                "embedding_cid": embedding_cid,
                "content": content
            }

            try:
                self.vector_db_manager.insert_document(
                    db_name, embedding_vector, metadata, embedding_cid)
                self.logger.info(
                    f"Inserted document into '{db_name}' with CID {embedding_cid}")
            except Exception as e:
                self.logger.error(
                    f"Failed to insert document into '{db_name}': {e}")


def main():
    """
    Main function to create and populate the database from IPFS CIDs.
    """
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    graph = IPFSNeo4jGraph(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password
    )

    components = {
        "converter": ["openai"],
        "chunker": ["fixed_length"],
        "embedder": ["openai"]
    }

    # Create database directory
    project_root = Path(__file__).parent.parent
    db_path = project_root / "descidb" / "database"
    os.makedirs(db_path, exist_ok=True)

    vector_db_manager = VectorDatabaseManager(components, db_path=str(db_path))
    create_db = DatabaseCreator(graph, vector_db_manager)

    relationship_path = [
        "CONVERTED_BY_openai",
        "CHUNKED_BY_fixed_length",
        "EMBEDDED_BY_openai"
    ]

    db_name = "openai_fixed_length_openai"

    # Look for cids.txt file in project root and temp directories
    cids_file_paths = [
        project_root / "cids.txt",
        project_root / "temp" / "cids.txt"
    ]

    cids_file = None
    for path in cids_file_paths:
        if path.exists():
            cids_file = path
            break

    if cids_file is None:
        logger.error("No cids.txt file found. Please run processor first.")
        return

    with open(cids_file, "r") as file:
        counter = 0
        for line in file:
            start_cid = line.strip()
            if start_cid:
                logger.info(f"Processing CID #{counter}: {start_cid}")
                create_db.process_paths(start_cid, relationship_path, db_name)
                counter += 1


if __name__ == "__main__":
    main()
