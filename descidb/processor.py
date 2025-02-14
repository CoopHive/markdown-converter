import json
import os
from typing import List

import requests

from descidb.chunker import chunk
from descidb.converter import convert
from descidb.embedder import embed
from descidb.Postgres import PostgresDBManager
from descidb.TokenRewarder import TokenRewarder
from descidb.utils import upload_to_lighthouse
from descidb.ChromaClient import VectorDatabaseManager
from descidb.GraphDB import IPFSNeo4jGraph
import subprocess


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
        self.metadata_file = metadata_file
        self.authorPublicKey = authorPublicKey  # Author Public Key
        self.ipfs_api_key = ipfs_api_key  # IPFS API Key
        self.postgres_db_manager = postgres_db_manager  # Postgres DB Manager
        self.convert_cache = {}  # Cache for converted text
        self.chunk_cache = {}  # Cache for chunked text
        self.graph_db = IPFSNeo4jGraph(uri=os.getenv("NEO4J_URI"), username=os.getenv(
            "NEO4J_USER"), password=os.getenv("NEO4J_PASSWORD"))
        self.__write_to_file(
            self.authorPublicKey, os.path.join(os.getcwd(), "tmp.txt"))
        self.author_cid = self.__upload_text_to_lighthouse(
            os.path.join(os.getcwd(), "tmp.txt")).split("ipfs/")[-1]
        self.graph_db.add_ipfs_node(self.author_cid)

    def __upload_text_to_lighthouse(self, filename: str) -> str:
        """Uploads a string as a file to Lighthouse IPFS and returns the IPFS hash (CID).

        - content: The string content to be uploaded.
        - filename: The name of the file for the uploaded content.
        - Returns: IPFS hash (CID) of the uploaded file.
        """
        url = "https://node.lighthouse.storage/api/v0/add"

        headers = {"Authorization": f"Bearer {self.ipfs_api_key}"}

        with open(filename, "rb") as file:
            files = {"file": file}
            response = requests.post(url, headers=headers, files=files)

        response.raise_for_status()

        return response.json()["Hash"]

    def __create_file_with_ipfs(self, content: str, file_path: str) -> str:
        """Creates a file with the IPFS CID and returns the CID.

        - content: The string content to be uploaded.
        - file_path: The name of the file for the uploaded content.
        - Returns: IPFS hash (CID) of the uploaded file.
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                file.write(content)
        except Exception as e:
            print(f"Error creating file: {e}")

    def __lighthouse_and_commit(self, object: str, git_path: str) -> str:
        """Uploads a file to Lighthouse IPFS and commits the CID to git.

        - object: Path to the object to be uploaded.
        - Returns: IPFS hash (CID) of the uploaded file.
        """
        try:
            ipfs_cid = self.__upload_text_to_lighthouse(object)

            hash_value = ipfs_cid.split("ipfs/")[-1]

            file_path = os.path.join(git_path, f"{hash_value}.txt")

            self.__create_file_with_ipfs(ipfs_cid, file_path)

            subprocess.run(
                ["git", "-C", git_path, "add", file_path], check=True)
            subprocess.run(["git", "-C", git_path, "commit",
                           "-m", f"Added IPFS CID: {hash_value}"], check=True)

            return ipfs_cid

        except Exception as e:
            print(f"Error during Git commit process: {e}")

    def __write_to_file(self, content: str, file_path: str):
        """Writes the content to a file.

        - content: The content to be written to the file.
        - file_path: The path to the file to write the content to.
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                file.write(content)
        except Exception as e:
            print(f"Error writing to file: {e}")

    def process(self, pdf_path: str, databases: List[dict], git_path: str):
        """Processes the PDF according to the list of database configurations passed.

        - pdf_path: Path to the input PDF.
        - databases: A list of JSON-like dicts, each containing a specific converter, chunker, and embedder.
        """
        doc_id = os.path.splitext(os.path.basename(pdf_path))[0]
        self.convert_cache = {}
        self.chunk_cache = {}
        tmp_file_path = os.path.join(os.getcwd(), "tmp.txt")

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
        metadata["pdf_ipfs_cid"] = self.__lighthouse_and_commit(
            object=pdf_path, git_path=git_path)

        self.graph_db.add_ipfs_node(metadata["pdf_ipfs_cid"])
        self.graph_db.create_relationship(metadata["pdf_ipfs_cid"],
                                          self.author_cid, "AUTHORED_BY")

        cid_file_path = os.path.join(os.getcwd(), "cids.txt")

        with open(cid_file_path, "a") as cid_file:
            cid_file.write(metadata["pdf_ipfs_cid"] + "\n")

        for db_config in databases:
            converter_func = db_config["converter"]
            chunker_func = db_config["chunker"]
            embedder_func = db_config["embedder"]

            # Step 2.1: Conversion
            if converter_func not in self.convert_cache:
                converted_text = convert(
                    conversion_type=converter_func, input_path=pdf_path
                )
                self.convert_cache[converter_func] = converted_text
            else:
                converted_text = self.convert_cache[converter_func]

            # Upload converted text to IPFS and commit to Git
            self.__write_to_file(converted_text, tmp_file_path)

            converted_text_ipfs_cid = self.__lighthouse_and_commit(
                object=tmp_file_path, git_path=git_path)

            self.graph_db.add_ipfs_node(converted_text_ipfs_cid)
            self.graph_db.create_relationship(
                metadata["pdf_ipfs_cid"], converted_text_ipfs_cid, "CONVERTED_BY_" + converter_func)
            self.graph_db.create_relationship(
                converted_text_ipfs_cid, self.author_cid, "AUTHORED_BY")
            # Step 2.2: Chunking
            chunk_cache_key = f"{converter_func}_{chunker_func}"
            if chunk_cache_key not in self.chunk_cache:
                chunked_text = chunk(
                    chunker_type=chunker_func, input_text=converted_text
                )
                self.chunk_cache[chunk_cache_key] = chunked_text
            else:
                chunked_text = self.chunk_cache[chunk_cache_key]

            for chunk_index, chunk_i in enumerate(chunked_text):

                self.__write_to_file(chunk_i, tmp_file_path)

                chunk_text_ipfs_cid = self.__lighthouse_and_commit(
                    object=tmp_file_path, git_path=git_path)

                self.graph_db.add_ipfs_node(chunk_text_ipfs_cid)
                self.graph_db.create_relationship(
                    converted_text_ipfs_cid, chunk_text_ipfs_cid, "CHUNKED_BY_" + chunker_func)
                self.graph_db.create_relationship(
                    chunk_text_ipfs_cid, self.author_cid, "AUTHORED_BY")
                # Step 2.3: Embedding

                embedding = embed(
                    embeder_type=embedder_func, input_text=chunk_i)

                self.__write_to_file(json.dumps(embedding), tmp_file_path)

                embedding_ipfs_cid = self.__lighthouse_and_commit(
                    object=tmp_file_path, git_path=git_path)
                self.graph_db.add_ipfs_node(embedding_ipfs_cid)
                self.graph_db.create_relationship(
                    chunk_text_ipfs_cid, embedding_ipfs_cid, "EMBEDDED_BY_" + embedder_func)
                self.graph_db.create_relationship(
                    embedding_ipfs_cid, self.author_cid, "AUTHORED_BY")
                # db_name = f"{converter_func}_{chunker_func}_{embedder_func}"
                # metadata.update(
                #     {
                #         "convert_method": converter_func,
                #         "chunk_method": chunker_func,
                #         "embed_method": embedder_func,
                #         "chunk_index": chunk_index,
                #     }
                # )

                # self.db_manager.insert_document(
                #     db_name=db_name,
                #     embedding=embedding,
                #     metadata=metadata,
                #     doc_id=f"{doc_id}_chunk_{chunk_index}",
                # )

                # self.postgres_db_manager.insert_data(
                #     db_name=db_name,
                #     data=[
                #         (
                #             self.authorPublicKey,
                #             metadata.get("title", "Unknown Title"),
                #             chunk_i,
                #             embedding,
                #             json.dumps(metadata),
                #             False,
                #         )
                #     ],
                # )
                # self.TokenRewarder.add_reward_to_user(
                #     public_key=self.authorPublicKey, db_name=db_name
                # )

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
