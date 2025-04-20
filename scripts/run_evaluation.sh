#!/bin/bash
# run_evaluation.sh
# DESCRIPTION: Query multiple ChromaDB collections with a prompt and rank the results via an LLM

set -e

echo "Running DeSciDB evaluation agent..."
poetry run python -m descidb.query.evaluation_main 