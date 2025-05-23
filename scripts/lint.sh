#!/bin/bash
# lint.sh
# DESCRIPTION: Run Black, isort, Flake8, and MyPy on src/ and tests/ for full style + type checks
set -e

echo "Running black formatter..."
poetry run black descidb tests

echo "Running isort..."
poetry run isort descidb tests

echo "Running flake8..."
poetry run flake8 descidb tests

echo "Running mypy..."
poetry run mypy descidb 