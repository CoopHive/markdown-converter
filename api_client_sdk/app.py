from flask import Flask, request, jsonify
import chromadb
from openai import OpenAI
import secrets
import sqlite3
from functools import wraps

OPENAI_API_KEY = "sk-proj-OqH5ok75imwtsbJKZrH7T3BlbkFJK9fL3mmdg5e4uryrf9vd"

app = Flask(__name__)


def generate_api_key(user_id):
    api_key = secrets.token_hex(32)
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO api_keys (user_id, api_key) VALUES (?, ?)", (user_id, api_key))
    conn.commit()
    conn.close()
    return api_key


def get_api_key_from_db(api_key):
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_keys WHERE api_key=?", (api_key,))
    result = cursor.fetchone()
    conn.close()
    return result


def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or not get_api_key_from_db(api_key):
            return jsonify({"error": "Forbidden"}), 403
        return func(*args, **kwargs)
    return wrapper


@app.route('/collections/<collection_name>/query', methods=['POST'])
@require_api_key
def query_collection(collection_name):
    openaiClient = OpenAI(api_key=OPENAI_API_KEY)

    data = request.json
    user_query = data.get('user_query')

    client = chromadb.HttpClient(
        host='localhost', port=8000)

    collection = client.get_or_create_collection(
        name=f"{collection_name}")

    model_name = "text-embedding-3-small"

    response = openaiClient.embeddings.create(
        model=model_name, input=[user_query])
    embedding = response.data[0].embedding

    values = collection.query(
        query_embeddings=[embedding],
        n_results=2,
    )

    all_documents = collection.get(include=['documents', 'metadatas'])
    print(f"All documents in collection: {all_documents}")

    return jsonify(values)


@app.route('/generate_key', methods=['POST'])
def generate_key():
    data = request.json
    user_id = data.get('user_id')
    if not user_id or not is_authenticated_user(user_id):
        return jsonify({"error": "Unauthorized"}), 401

    new_key = generate_api_key(user_id)
    return jsonify({"api_key": new_key})


def is_authenticated_user(user_id):
    # Implement logic for user authentication (payments/stripe, etc.)
    return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
