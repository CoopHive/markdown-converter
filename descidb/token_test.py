"""
Token reward testing module for DeSciDB.

This module provides functionality to test token rewards by fetching author statistics
from Neo4j and distributing rewards based on their contributions.
"""

from descidb.token_rewarder import TokenRewarder
from descidb.graph_db import IPFSNeo4jGraph
from pathlib import Path
import os


def run_reward_users():
    """
    Run a test of the token reward system.

    This function connects to Neo4j, fetches author contribution statistics,
    and distributes token rewards based on their contributions across different databases.
    """
    # Initialize Neo4j graph connection
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    graph = IPFSNeo4jGraph(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password
    )

    # Fetch author job contributions from Neo4j
    author_jobs = graph.get_authored_by_stats()

    # # Define database configurations
    databases = [
        {"converter": "openai", "chunker": "paragraph", "embedder": "openai"},
    ]

    # # Extract components
    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases])),
    }

    # Get project root directory
    project_root = Path(__file__).parent.parent
    contract_abi_path = project_root / "contracts" / "CoopHiveV1.json"

    # Initialize the TokenRewarder
    rewarder = TokenRewarder(
        network="test_base",
        contract_address="0x3bB10ec2404638c6fB9f98948f8e3730316B7BfA",
        contract_abi_path=str(contract_abi_path),
        db_components=components,
        host="localhost",
        port=5432,
        user="vardhanshorewala",
        password="password",
    )

    # Add users and update their job counts
    for author_id, job_count in author_jobs.items():
        for db_config in databases:
            db_name = f"{db_config['converter']}_{db_config['chunker']}_{db_config['embedder']}"
            rewarder.add_reward_to_user(
                str(author_id), db_name, job_count)
            print(f"Added/Updated user {author_id} in {db_name}")

    # Now reward users
    rewarder.get_user_rewards("openai_paragraph_openai_token")


if __name__ == "__main__":
    run_reward_users()
