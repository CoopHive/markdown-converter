#!/bin/bash
# Test the evaluation endpoint

# Default values
PORT=3000
HOST="localhost"
QUERY="What is MINT-DFC"
COLLECTIONS=("openai_paragraph_openai" "openai_fixed_length_openai" "marker_paragraph_openai" "marker_fixed_length_openai")
MODEL="openai/gpt-3.5-turbo-0613"

# Create JSON payload
JSON_PAYLOAD=$(cat << EOF
{
  "query": "$QUERY",
  "collections": $(printf '%s\n' "${COLLECTIONS[@]}" | jq -R . | jq -s .),
  "db_path": null,
  "model_name": "$MODEL"
}
EOF
)

# Display the payload
echo "Sending request with payload:"
echo "$JSON_PAYLOAD" | jq .

# Send the request
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" \
  "http://$HOST:$PORT/api/evaluate" | jq . 