#!/bin/bash
# run_processor.sh
# DESCRIPTION: End‑to‑end pipeline — PDF → Markdown → chunks → embeddings → IPFS/DB
set -e

echo "Running DeSciDB processor..."
poetry run python -m descidb.core.processor_main -v 