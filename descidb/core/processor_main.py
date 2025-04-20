"""
Main module for the DeSciDB package.

This module contains the entry point for the DeSciDB processor, which handles
PDF processing, conversion, chunking, embedding, and storage in various databases.
"""

import hashlib
import os
import subprocess
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv

from descidb.core.chunker import chunk_from_url
from descidb.core.embedder import embed_from_url
from descidb.core.processor import Processor
from descidb.db.chroma_client import VectorDatabaseManager
from descidb.db.postgres_db import PostgresDBManager
from descidb.rewards.token_rewarder import TokenRewarder
from descidb.utils.logging_utils import get_logger
from descidb.utils.utils import compress, upload_to_lighthouse

# Get module logger
logger = get_logger(__name__)

load_dotenv(override=True)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
# Parent directory of the project (coophive folder)
COOPHIVE_DIR = PROJECT_ROOT.parent


def load_config():
    """
    Load configuration from the config file.

    Returns:
        dict: Configuration dictionary
    """
    config_path = PROJECT_ROOT / "config" / "processor.yml"

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        raise


def test_processor():
    """
    Test the document processing pipeline with sample papers.
    """
    # Load configuration
    config = load_config()

    # Process configuration
    processing_config = config["processing"]
    postgres_config = config["postgres"]
    author_config = config["author"]
    api_keys = config["api_keys"]

    # Setup paths
    papers_directory = PROJECT_ROOT / processing_config["papers_directory"]
    metadata_file = PROJECT_ROOT / processing_config["metadata_file"]
    storage_directory = COOPHIVE_DIR / processing_config["storage_directory"]

    # Setup API keys and database connection
    lighthouse_api_key = os.getenv(api_keys["lighthouse_token"].replace("${", "").replace("}", ""))

    db_manager_postgres = PostgresDBManager(
        host=postgres_config["host"],
        port=postgres_config["port"],
        user=postgres_config["user"],
        password=postgres_config["password"],
    )

    # Get papers
    papers = [
        os.path.join(papers_directory, f)
        for f in os.listdir(papers_directory)
        if f.endswith(".pdf")
    ][:processing_config["max_papers"]]

    # Setup database configurations
    databases = config["databases"]

    # Extract components from database configurations
    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases])),
    }

    db_manager = VectorDatabaseManager(components=components)

    tokenRewarder = TokenRewarder(
        db_components=components,
        host=postgres_config["host"],
        port=postgres_config["port"],
        user=postgres_config["user"],
        password=postgres_config["password"],
    )

    # Generate db_names from configurations
    for db_config in databases:
        converter = db_config["converter"]
        chunker = db_config["chunker"]
        embedder = db_config["embedder"]

        db_name = f"{converter}_{chunker}_{embedder}"
        db_config["db_name"] = db_name

    db_names = [db_config["db_name"] for db_config in databases]

    db_manager_postgres.create_databases(db_names)

    processor = Processor(
        authorPublicKey=author_config["public_key"],
        db_manager=db_manager,
        postgres_db_manager=db_manager_postgres,
        metadata_file=str(metadata_file),
        ipfs_api_key=lighthouse_api_key,
        TokenRewarder=tokenRewarder,
        project_root=PROJECT_ROOT,
    )

    for paper in papers:
        logger.info(f"Processing {paper}...")
        random_data = os.urandom(32)
        hash_value = hashlib.sha256(random_data).hexdigest()

        paper_dir = storage_directory / hash_value
        try:
            os.makedirs(paper_dir, exist_ok=True)
            # Store the current directory
            current_dir = os.getcwd()
            # Change to the paper directory for git operations
            os.chdir(paper_dir)
            subprocess.run(["git", "init"], check=True)
            # Change back to the original directory after git init
            os.chdir(current_dir)
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            continue

        processor.process(pdf_path=paper, databases=databases, git_path=str(paper_dir))

        time.sleep(5)


if __name__ == "__main__":
    logger.info("Running test_processor")
    test_processor()
