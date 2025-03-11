import logging
import requests
import json
from descidb.GraphDB import IPFSNeo4jGraph
from descidb.ChromaClient import VectorDatabaseManager
import dotenv

dotenv.load_dotenv()


class CreateDB:
    def __init__(self, graph, vector_db_manager):
        self.graph = graph
        self.vector_db_manager = vector_db_manager

    def query_lighthouse_for_embedding(self, cid):
        url = f"https://gateway.lighthouse.storage/ipfs/{cid}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            embedding_vector = json.loads(response.text)
            return embedding_vector
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.error(f"Failed to retrieve embedding for CID {cid}: {e}")
            return None

    def query_ipfs_content(self, cid):
        url = f"https://gateway.lighthouse.storage/ipfs/{cid}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            return content
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Failed to retrieve IPFS content for CID {cid}: {e}")
            return None

    def process_paths(self, start_cid, path, db_name):
        paths = self.graph.recreate_path(start_cid, path)
        print(len(paths))
        if not paths:
            logging.error(f"No valid paths found for CID {start_cid}")
            return

        for path_nodes in paths:
            if len(path_nodes) < 2:
                logging.error(f"Path {path_nodes} is too short.")
                continue

            content_cid = path_nodes[-2]
            embedding_cid = path_nodes[-1]

            embedding_vector = self.query_lighthouse_for_embedding(
                embedding_cid)
            if embedding_vector is None:
                logging.error(
                    f"Skipping path {path_nodes} due to failed embedding retrieval.")
                continue

            content = self.query_ipfs_content(content_cid)
            if content is None:
                logging.error(
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
                logging.info(
                    f"Inserted document into '{db_name}' with CID {embedding_cid}")
            except Exception as e:
                logging.error(
                    f"Failed to insert document into '{db_name}': {e}")


def main():
    graph = IPFSNeo4jGraph(
            uri="bolt://b191b806.databases.neo4j.io:7687", 
            username="neo4j", 
            password="3a9zR8-u38Vn7x8WWerccZUxN8eSNRVD_cyc33C7j1Y"
        )

    components = {
        "converter": ["openai"],
        "chunker": ["fixed_length"],
        "embedder": ["openai"]
    }
    vector_db_manager = VectorDatabaseManager(components)
    create_db = CreateDB(graph, vector_db_manager)

    relationship_path = ["CONVERTED_BY_openai",
                         "CHUNKED_BY_fixed_length", "EMBEDDED_BY_openai"]
    
    db_name = "openai_fixed_length_openai"

    with open("cids.txt", "r") as file:
        counter = 0
        for line in file:
            start_cid = line.strip()
            if start_cid:
                print(counter)
                logging.info(f"Processing CID: {start_cid}")
                create_db.process_paths(start_cid, relationship_path, db_name)
                counter += 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
