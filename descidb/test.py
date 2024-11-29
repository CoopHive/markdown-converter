import os
from processor import Processor
from vectordb import VectorDatabaseManager

from Postgres import PostgresDBManager
from TokenRewarder import TokenRewarder


def test_processor_with_real_data():
    papers_directory = "../papers"
    metadata_file = "metadata.json"
    max_papers = 2

    lighthouse_api_key = "ENTER_API_KEY_HERE"
    postgres_host = "localhost"
    postgres_port = 5432
    postgres_user = "vardhanshorewala"
    postgres_password = "password"

    db_manager_postgres = PostgresDBManager(
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password
    )

    papers = [os.path.join(papers_directory, f) for f in os.listdir(
        papers_directory) if f.endswith('.pdf')][:max_papers]

    databases = [
        {
            "converter": "openai",
            "chunker": "sentence",
            "embedder": "openai"
        },
        {
            "converter": "openai",
            "chunker": "paragraph",
            "embedder": "openai"
        }
    ]

    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases]))
    }

    db_manager = VectorDatabaseManager(components=components)

    tokenRewarder = TokenRewarder(db_components=components, host=postgres_host, port=postgres_port,
                                  user=postgres_user, password=postgres_password)

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
        metadata_file=metadata_file,
        ipfs_api_key=lighthouse_api_key,
        TokenRewarder=tokenRewarder
    )

    for paper in papers:
        print(f"Processing {paper}...")
        processor.process(pdf_path=paper, databases=databases)

    # tokenRewarder.reward_users()


if __name__ == '__main__':
    test_processor_with_real_data()
