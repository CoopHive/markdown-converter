#!/bin/bash
set -e

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install it first."
    echo "You can install it by running: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies if needed
if [ "$1" == "install" ]; then
    echo "Installing dependencies..."
    poetry install
    exit 0
fi

# Run tests with coverage
if [ "$1" == "test" ] || [ "$1" == "" ]; then
    echo "Running tests with coverage..."
    poetry run pytest
    exit 0
fi

# Run specific test file
if [ "$1" == "file" ] && [ -n "$2" ]; then
    echo "Running tests in file $2..."
    poetry run pytest "$2" -v
    exit 0
fi

# Run linting
if [ "$1" == "lint" ]; then
    echo "Running linting..."
    poetry run black descidb tests
    poetry run isort descidb tests
    poetry run flake8 descidb tests
    poetry run mypy descidb
    exit 0
fi

# Run individual linting commands
if [ "$1" == "black" ]; then
    echo "Running black formatter..."
    poetry run black descidb tests
    exit 0
fi

if [ "$1" == "isort" ]; then
    echo "Running isort..."
    poetry run isort descidb tests
    exit 0
fi

if [ "$1" == "flake8" ]; then
    echo "Running flake8..."
    poetry run flake8 descidb tests
    exit 0
fi

if [ "$1" == "mypy" ]; then
    echo "Running mypy..."
    poetry run mypy descidb
    exit 0
fi

# Show help
echo "Usage: ./run-tests.sh [command]"
echo ""
echo "Commands:"
echo "  install       Install dependencies using Poetry"
echo "  test          Run all tests with coverage (default)"
echo "  file <path>   Run tests in a specific file"
echo "  lint          Run all linting tools"
echo "  black         Run black formatter only"
echo "  isort         Run isort only"
echo "  flake8        Run flake8 only"
echo "  mypy          Run mypy only"
echo "" 