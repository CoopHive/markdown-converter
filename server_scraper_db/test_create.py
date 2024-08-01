import os
import chromadb
from openai import OpenAI
import sqlite3
from db import DocumentDatabase

OPENAI_API_KEY = "sk-proj-OqH5ok75imwtsbJKZrH7T3BlbkFJK9fL3mmdg5e4uryrf9vd"
DB_HOST = "localhost"
DB_PORT = 8000
DATABASE_NAME = "dvd_sentence_openai"

# Initialize the DocumentDatabase
doc_db = DocumentDatabase(openai_api_key=OPENAI_API_KEY,
                          db_host=DB_HOST, db_port=DB_PORT)

# Create or retrieve the collections
collection_openai, collection_nvidia = doc_db.create_database(DATABASE_NAME)

# Print all documents in the OpenAI collection
print("OpenAI Collection:")
doc_db.print_all_documents(embed_strategy='openai')


# client = OpenAI(api_key=OPENAI_API_KEY)


# def create_database(databasename, version):
#     client = chromadb.HttpClient(
#         host='localhost', port=8000)  # Server IP and port
#     collection = client.get_or_create_collection(
#         name=f"{databasename}v{version}")
#     return collection


# def paragraph_to_openai_input(paragraph, model="text-embedding-ada-002"):
#     response = client.embeddings.create(model=model, input=[paragraph])
#     embedding = response.data[0].embedding
#     return embedding


# def insert_fruit_facts(collection, facts):
#     for i, fact in enumerate(facts):
#         embedded_fact = paragraph_to_openai_input(fact)
#         collection.add(
#             documents=[fact],
#             embeddings=[embedded_fact],
#             ids=[f"fact_{i}"],
#             metadatas=[{"fact_index": i}]
#         )
#     print("Fruit facts added to the collection successfully.")


# def main():
#     # Create the database/collection
#     collection = create_database(databasename="fruitdb", version="1.0")

#     # Define some random facts about different fruits
#     fruit_facts = [
#         "Apples are made of 25% air, which is why they float.",
#         "Bananas are berries, but strawberries aren't.",
#         "Cherries are a member of the rose family.",
#         "Grapes explode when you put them in the microwave.",
#         "Lemons contain more sugar than strawberries.",
#         "Oranges are not naturally occurring fruits but are hybrids.",
#         "Pineapples take about two years to grow.",
#         "A strawberry has about 200 seeds on its surface.",
#         "Watermelons are 92% water.",
#         "Peaches and nectarines are essentially the same fruit, one with fuzz and one without."
#     ]

#     # Insert fruit facts into the collection
#     insert_fruit_facts(collection, fruit_facts)


# if __name__ == "__main__":
#     main()
