import os
import certifi
import logging
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)


class IPFSNeo4jGraph:
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection with SSL certification."""
        try:
            os.environ["SSL_CERT_FILE"] = certifi.where()

            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            logging.info("Successfully connected to Neo4j AuraDB")
        except Exception as e:
            logging.error(f"Connection error: {e}")
            raise

    def close(self):
        """Close the database connection."""
        self.driver.close()
        logging.info("Database connection closed.")

    def add_ipfs_node(self, cid):
        """Add an IPFS CID as a node in Neo4j."""
        try:
            with self.driver.session() as session:
                session.run("MERGE (:IPFS {cid: $cid})", cid=cid)
                logging.info(f"Node added: {cid}")
        except Exception as e:
            logging.error(f"Failed to add node {cid}: {e}")

    def create_relationship(self, cid1, cid2, relationship_type="LINKS_TO"):
        """Create a relationship between two IPFS nodes (avoiding Cartesian Product)."""
        try:
            with self.driver.session() as session:
                query = f"""
                    MERGE (a:IPFS {{cid: $cid1}})
                    MERGE (b:IPFS {{cid: $cid2}})
                    MERGE (a)-[:{relationship_type}]->(b)
                """
                session.run(query, cid1=cid1, cid2=cid2)
                logging.info(f"Relationship created: {
                    cid1} -[{relationship_type}]-> {cid2}")
        except Exception as e:
            logging.error(f"Failed to create relationship {
                cid1} -[{relationship_type}]-> {cid2}: {e}")

    def query_graph(self):
        """Retrieve all nodes and relationships."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (a)-[r]->(b) RETURN a.cid, TYPE(r), b.cid")
                for record in result:
                    print(
                        f"{record['a.cid']} -[{record['TYPE(r)']}]→ {record['b.cid']}")
        except Exception as e:
            logging.error(f"Failed to query graph: {e}")

    def recreate_path(self, start_cid, path):
        """
        Given a starting node and an ordered list of relationship steps,
        return all possible paths with intermediate nodes included.

        :param start_cid: The CID of the starting node.
        :param path: Ordered list of relationship types to follow.
        :return: List of lists, where each list represents a path including intermediate nodes.
        """
        if not path:
            return [[start_cid]]

        try:
            with self.driver.session() as session:
                query = "MATCH (start:IPFS {cid: $start_cid})"
                path_return = ["start.cid"]

                for i, rel in enumerate(path):
                    query += f"-[:{rel}]->(n{i}:IPFS)"
                    path_return.append(f"n{i}.cid")

                query += f" RETURN {', '.join(path_return)}"

                result = session.run(query, start_cid=start_cid)
                paths = [[record[key] for key in path_return]
                         for record in result]

                return paths if paths else False
        except Exception as e:
            logging.error(f"Failed to traverse path from {
                          start_cid} with path {path}: {e}")
            return False

    def traverse_path_end_nodes(self, start_cid, path):
        """
        Given a starting node and an ordered list of relationship steps, 
        return all node CIDs that exist at the end of the given path.

        :param start_cid: The CID of the starting node.
        :param path: Ordered list of relationship types to follow.
        :return: List of node CIDs at the end of the path if exists, else False.
        """
        if not path:
            return [start_cid]

        try:
            with self.driver.session() as session:
                query = "MATCH (start:IPFS {cid: $start_cid})"
                for i, rel in enumerate(path):
                    query += f"-[:{rel}]->(n{i}:IPFS)"
                query += f" RETURN n{len(path)-1}.cid AS end_cid"

                result = session.run(query, start_cid=start_cid)
                end_nodes = [record["end_cid"] for record in result]

                return end_nodes if end_nodes else False
        except Exception as e:
            logging.error(f"Failed to traverse path from {
                          start_cid} with path {path}: {e}")
            return False


# graph = IPFSNeo4jGraph(uri="bolt+s://9fb20fc2.databases.neo4j.io:7687",
#                        username="neo4j", password="z2-Aq8cYB0BN7HM54BDCYgoepzrPcqLexdmbUawm_pg")

# # Sample data
# graph.add_ipfs_node("A")
# graph.add_ipfs_node("B1")
# graph.add_ipfs_node("B2")
# graph.add_ipfs_node("C1")
# graph.add_ipfs_node("C2")

# graph.create_relationship("A", "B1", "LINKS_TO")
# graph.create_relationship("A", "B2", "LINKS_TO")
# graph.create_relationship("A", "B3", "LINKS_TO")
# graph.create_relationship("B1", "C1", "STORED_IN")
# graph.create_relationship("B2", "C2", "STORED_IN")
# graph.create_relationship("B2", "C3", "STORED_IN")

# result = graph.recreate_path("A", ["LINKS_TO", "STORED_IN"])
# print(result)

# graph.close()
