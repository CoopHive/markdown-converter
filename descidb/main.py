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

from dotenv import load_dotenv

from descidb.chroma_client import VectorDatabaseManager
from descidb.chunker import chunk_from_url
from descidb.embedder import embed_from_url
from descidb.logging_utils import get_logger
from descidb.postgres_db import PostgresDBManager
from descidb.processor import Processor
from descidb.token_rewarder import TokenRewarder
from descidb.utils import compress, upload_to_lighthouse

# Get module logger
logger = get_logger(__name__)

load_dotenv(override=True)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
# Parent directory of the project (coophive folder)
COOPHIVE_DIR = PROJECT_ROOT.parent


def test_processor():
    """
    Test the document processing pipeline with sample papers.
    """
    papers_directory = PROJECT_ROOT / "papers"
    metadata_file = papers_directory / "metadata.json"
    storage_directory = COOPHIVE_DIR / "papers-graph-demo"

    max_papers = 10

    lighthouse_api_key = os.getenv("LIGHTHOUSE_TOKEN")
    postgres_host = "localhost"
    postgres_port = 5432
    postgres_user = "vardhanshorewala"
    postgres_password = "password"

    db_manager_postgres = PostgresDBManager(
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
    )

    papers = [
        os.path.join(papers_directory, f)
        for f in os.listdir(papers_directory)
        if f.endswith(".pdf")
    ][:max_papers]

    databases = [
        {
            "converter": "openai",
            "chunker": "fixed_length",
            "embedder": "openai",
        },
    ]

    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases])),
    }

    db_manager = VectorDatabaseManager(components=components)

    tokenRewarder = TokenRewarder(
        db_components=components,
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
    )

    for db_config in databases:
        converter = db_config["converter"]
        chunker = db_config["chunker"]
        embedder = db_config["embedder"]

        db_name = f"{converter}_{chunker}_{embedder}"
        db_config["db_name"] = db_name

    db_names = [db_config["db_name"] for db_config in databases]

    db_manager_postgres.create_databases(db_names)

    processor = Processor(
        authorPublicKey="0x55DE19820d5Dfc5761370Beb16Eb041E11272619",
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
