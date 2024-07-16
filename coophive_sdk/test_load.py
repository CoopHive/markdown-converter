from coophive_sdk import CoopHiveClient

# Initialize the client
client = CoopHiveClient()

# Test the query function
database_name = "fruitdb"
user_query = "What is the fact about apples?"
response = client.queries.query_database(database_name, user_query)

print(response)
