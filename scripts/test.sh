#!/bin/bash
# test.sh
# DESCRIPTION: Execute pytest suite with coverage output

set -e

# Check if a specific file is provided
if [ -n "$1" ]; then
    echo "Running tests in file $1..."
    poetry run pytest "$1" -v
else
    echo "Running all tests with coverage..."
    poetry run pytest
fi 