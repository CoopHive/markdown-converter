from descidb.TokenRewarder import TokenRewarder
from descidb.GraphDB import IPFSNeo4jGraph


def run_reward_users():
    # Initialize Neo4j graph connection
    graph = IPFSNeo4jGraph(
        uri="bolt+s://9fb20fc2.databases.neo4j.io:7687",
        username="neo4j",
        password="z2-Aq8cYB0BN7HM54BDCYgoepzrPcqLexdmbUawm_pg"
    )

    # Fetch author job contributions from Neo4j
    author_jobs = graph.get_authored_by_stats()

    # Define database configurations
    databases = [
        {"converter": "openai", "chunker": "paragraph", "embedder": "openai"},
    ]

    # Extract components
    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases])),
    }

    # Initialize the TokenRewarder
    rewarder = TokenRewarder(
        network="test_base",
        contract_address="0x14436f6895B8EC34e0E4994Df29D1856b665B490",
        contract_abi_path="/Users/vardhanshorewala/Desktop/coophive/markdown-converter/contracts/CoopHiveV1.json",
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
