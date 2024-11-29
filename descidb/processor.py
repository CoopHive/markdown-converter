import json
import os
from typing import List

import requests
from chunker import Chunker
from converter import Converter
from embedder import Embedder
from Postgres import PostgresDBManager
from TokenRewarder import TokenRewarder
from vectordb import VectorDatabaseManager


class Processor:
    def __init__(
        self,
        authorPublicKey: str,
        db_manager: VectorDatabaseManager,
        postgres_db_manager: PostgresDBManager,
        metadata_file: str,
        ipfs_api_key: str,
        TokenRewarder: TokenRewarder,
    ):
        """Initializes the Processor class with the necessary components.

        - db_manager: An instance of the VectorDatabaseManager to handle database operations.
        - metadata_file: Path to the metadata file for retrieving document information.
        - ipfs_api_key: API key for IPFS upload if required.
        """
        self.db_manager = db_manager  # Vector Database Manager
        self.TokenRewarder = TokenRewarder
        self.converter = Converter()  # Converter
        self.chunker = Chunker()  # Chunker
        self.embedder = Embedder()  # Embedder
        self.metadata_file = metadata_file  # Metadata File
        self.authorPublicKey = authorPublicKey  # Author Public Key
        self.ipfs_api_key = ipfs_api_key  # IPFS API Key
        self.postgres_db_manager = postgres_db_manager  # Postgres DB Manager
        self.convert_cache = {}  # Cache for converted text
        self.chunk_cache = {}  # Cache for chunked text

    def upload_to_lighthouse(self, filepath: str) -> str:
        """Uploads a file to Lighthouse IPFS and returns the IPFS hash (CID).

        - filepath: Path to the file to be uploaded.
        - Returns: IPFS hash (CID) of the uploaded file.
        """
        url = "https://node.lighthouse.storage/api/v0/add"
        headers = {"Authorization": f"Bearer {self.ipfs_api_key}"}
        with open(filepath, "rb") as file:
            files = {"file": file}
            print(f"Uploading {filepath} to Lighthouse IPFS...")
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()["Hash"]

    def upload_text_to_lighthouse(self, content: str, filename: str) -> str:
        """Uploads a string as a file to Lighthouse IPFS and returns the IPFS hash (CID).

        - content: The string content to be uploaded.
        - filename: The name of the file for the uploaded content.
        - Returns: IPFS hash (CID) of the uploaded file.
        """
        url = "https://node.lighthouse.storage/api/v0/add"
        headers = {"Authorization": f"Bearer {self.ipfs_api_key}"}
        files = {"file": (filename, content, "text/plain")}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()["Hash"]

    def process(self, pdf_path: str, databases: List[dict]):
        """Processes the PDF according to the list of database configurations passed.

        - pdf_path: Path to the input PDF.
        - databases: A list of JSON-like dicts, each containing a specific converter, chunker, and embedder.
        """
        doc_id = os.path.splitext(os.path.basename(pdf_path))[0]
        print(f"Processing document: {doc_id}")
        self.convert_cache = {}  # Cache for converted text
        self.chunk_cache = {}  # Cache for chunked text

        # Fetch metadata for the document
        metadata = self.get_metadata_for_doc(self.metadata_file, doc_id)
        if not metadata:
            metadata = self.default_metadata(doc_id)

        metadata = {
            key: (
                json.dumps(value)
                if isinstance(value, (list, dict))
                else value
                if value is not None
                else "N/A"
            )
            for key, value in metadata.items()
        }

        pdf_cid = self.upload_to_lighthouse(pdf_path)
        metadata["pdf_ipfs_cid"] = pdf_cid

        for db_config in databases:
            converter_func = db_config["converter"]
            chunker_func = db_config["chunker"]
            embedder_func = db_config["embedder"]

            # Step 2.1: Conversion
            if converter_func not in self.convert_cache:
                print(f"Running Converter({converter_func}) on {pdf_path}")
                convert_method = getattr(self.converter, converter_func)
                converted_text = convert_method(pdf_path)
                self.convert_cache[converter_func] = converted_text

            else:
                converted_text = self.convert_cache[converter_func]
                print(f"Using cached conversion for {converter_func}")

            chunk_cache_key = f"{converter_func}_{chunker_func}"
            if chunk_cache_key not in self.chunk_cache:
                print(
                    f"Running Chunker({chunker_func}) on converted text from {converter_func}"
                )
                chunk_method = getattr(self.chunker, chunker_func)
                chunked_text = chunk_method(converted_text)
                self.chunk_cache[chunk_cache_key] = chunked_text
            else:
                chunked_text = self.chunk_cache[chunk_cache_key]

            print(
                f"Running Embedder({embedder_func}) on chunked text from {chunker_func}"
            )
            embed_method = getattr(self.embedder, embedder_func)

            for chunk_index, chunk in enumerate(chunked_text):
                embedding = embed_method(chunk)

                db_name = f"{converter_func}_{chunker_func}_{embedder_func}"
                metadata.update(
                    {
                        "convert_method": converter_func,
                        "chunk_method": chunker_func,
                        "embed_method": embedder_func,
                        "chunk_index": chunk_index,
                    }
                )

                self.db_manager.insert_document(
                    db_name=db_name,
                    embedding=embedding,
                    metadata=metadata,
                    doc_id=f"{doc_id}_chunk_{chunk_index}",
                )

                self.postgres_db_manager.insert_data(
                    db_name=db_name,
                    data=[
                        (
                            self.authorPublicKey,
                            metadata.get("title", "Unknown Title"),
                            chunk,
                            embedding,
                            json.dumps(metadata),
                            False,
                        )
                    ],
                )
                self.TokenRewarder.add_reward_to_user(
                    public_key=self.authorPublicKey, db_name=db_name
                )

                print(f"Inserted chunk {chunk_index} into {db_name} database.")

    def get_metadata_for_doc(self, metadata_file: str, doc_id: str):
        """Retrieves metadata for the given document ID from the metadata file.

        - metadata_file: Path to the metadata file.
        - doc_id: Document ID to retrieve metadata for.
        """
        with open(metadata_file, "r") as file:
            for line in file:
                try:
                    data = json.loads(line)
                    if data.get("id") == doc_id:
                        return data
                except json.JSONDecodeError:
                    continue
        return {}

    def default_metadata(self, doc_id: str) -> dict:
        """Returns default metadata in case None is found.

        The metadata.json file aready exists for Arxiv papers.
        """
        return {
            "title": "Unknown Title",
            "authors": "Unknown Authors",
            "categories": "Unknown Categories",
            "abstract": "No abstract available.",
            "doi": "No DOI available",
        }
