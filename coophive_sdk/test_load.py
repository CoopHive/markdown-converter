from coophive_sdk import CoopHiveClient

api_key = "sfnlsdn"

client = CoopHiveClient(api_key=api_key)

database_name = "fruitdb"
user_query = "What is the fact about apples?"
response = client.queries.query_database(database_name, user_query)

print(response)
