import os

from dotenv import load_dotenv
from Postgres import PostgresDBManager
from processor import Processor
from TokenRewarder import TokenRewarder
from vectordb import VectorDatabaseManager
from utils import upload_to_lighthouse
from converter import Converter
load_dotenv(override=True)


def test_processor_with_real_data():
    papers_directory = "../papers"
    metadata_file = "../papers/metadata.json"
    max_papers = 1

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
        # {"converter": "openai", "chunker": "sentence", "embedder": "openai"},
        {
            "converter": "marker",
            "chunker": "paragraph",
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
        metadata_file=metadata_file,
        ipfs_api_key=lighthouse_api_key,
        TokenRewarder=tokenRewarder,
    )

    for paper in papers:
        print(f"Processing {paper}...")
        processor.process(pdf_path=paper, databases=databases)

    # tokenRewarder.reward_users()


def modular_pipeline():
    # First dockerfile expects url with (set of) pdf(s) and a converter type as input.
    pdf_path = "../papers/desci.pdf"
    lighthouse_api_key = os.getenv("LIGHTHOUSE_TOKEN")
    
    input_url = upload_to_lighthouse(pdf_path, lighthouse_api_key)
    converter_type = 'marker'

    # converter

    breakpoint()

    chunker = 'paragraph'

    embedder =  "openai"

if __name__ == "__main__":
    modular_pipeline()