from coophive_sdk import CoopHiveClient

api_key = "54eb2e62552770b4d5f898a43a45d1beaaf3583c56371e779d53a704b0fb77e0"

client = CoopHiveClient(api_key=api_key)

database_name = "dvd_paragraph_openai"
user_query = "REFERENCES"
response = client.queries.query_database(database_name, user_query)

print(response)
