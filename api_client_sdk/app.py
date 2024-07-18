from flask import Flask, request, jsonify
import chromadb
from openai import OpenAI
from stripe import StripeClient


OPENAI_API_KEY = "OPENAI_API_KEY"

app = Flask(__name__)

class PaymentClient:
    def __init__(self, flat_rate, currency):
        self.stripe_api_key = "STRIPE_API_KEY"
        self.stripe_client = StripeClient(api_key=self.stripe_api_key)
        self.flat_rate = flat_rate
        self.currency = currency

    async def create_payment_intent(self, account):
        async with self.stripe_client.PaymentIntent.create(
                amount=self.flat_rate,
                currency=self.currency,
                stripe_account=account,
                confirm=True
                ) as response:
            return await response.json()

@app.route('/collections/<collection_name>/query', methods=['POST'])
async def query_collection(collection_name):
    print(" ")
    print(" ")
    print(" ")
    print(" ")

    print(OPENAI_API_KEY)
    print("process request")
    print(" ")
    print(" ")
    print(" ")

    stripe_client = PaymentClient(1, "usd")
    openaiClient = OpenAI(api_key=OPENAI_API_KEY)

    data = request.json
    user_query = data.get('user_query')
    stipe_account = data.get('Stripe-Account')

    if not user_query:
        return jsonify({"error": "No user query provided"}), 400

    if not stipe_account:
        return jsonify({"error": "No Stripe account provided"}), 400


    stripe_intent_response = await stripe_client.create_payment_intent(stipe_account)

    if (response := stripe_intent_response.get("success")):
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

        print(values)
        return jsonify(values)
    else:
        return jsonify({"error": response}), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
