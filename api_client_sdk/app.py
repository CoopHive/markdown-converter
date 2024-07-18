from flask import Flask, request, jsonify
import chromadb
from openai import OpenAI

OPENAI_API_KEY = "OPENAI_API_KEY"

app = Flask(__name__)


@app.route('/collections/<collection_name>/query', methods=['POST'])
def query_collection(collection_name):
    openaiClient = OpenAI(api_key=OPENAI_API_KEY)

    data = request.json
    user_query = data.get('user_query')

    client = chromadb.HttpClient(
        host='localhost', port=8000)  # Server IP and port of the database in docker container

    collection = client.get_or_create_collection(
        name=f"{collection_name}v{'1.0'}")

    model = "text-embedding-ada-002"

    response = openaiClient.embeddings.create(model=model, input=[user_query])
    embedding = response.data[0].embedding

    values = collection.query(
        query_embeddings=[embedding],
        n_results=2,
    )

    return jsonify(values)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
