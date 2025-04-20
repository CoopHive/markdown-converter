#!/bin/bash
# setup.sh
# DESCRIPTION: Bootstrap the project — create venv/Poetry env and install all dependencies

set -e

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install it first."
    echo "You can install it by running: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "Installing dependencies..."
poetry install 