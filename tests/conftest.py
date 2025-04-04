"""
Configuration module for pytest.

This module contains fixtures and setup/teardown functions for tests.
"""

import os
import pytest
from unittest.mock import MagicMock
import tempfile


@pytest.fixture
def sample_text():
    """Return a sample text for testing."""
    return """This is paragraph 1. It has multiple sentences. Each should be identified correctly.

This is paragraph 2. It also has multiple sentences! And questions?

This is the final paragraph. Just one more sentence."""


@pytest.fixture
def temp_pdf_file():
    """Create a temporary file with .pdf extension for testing."""
    fd, path = tempfile.mkstemp(suffix='.pdf')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write("PDF content placeholder")
        yield path
    finally:
        # Cleanup the temp file after test completes
        os.unlink(path)


@pytest.fixture
def temp_tar_file():
    """Create a temporary file with .tar extension for testing."""
    fd, path = tempfile.mkstemp(suffix='.tar')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write("TAR content placeholder")
        yield path
    finally:
        # Cleanup the temp file after test completes
        os.unlink(path)


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response with an embedding."""
    mock_response = MagicMock()
    mock_data = MagicMock()
    mock_data.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_response.data = [mock_data]
    return mock_response


@pytest.fixture
def mock_environment_variables():
    """Set up and tear down environment variables for testing."""
    # Store original environment variables
    original_values = {}
    test_vars = {
        "OPENAI_API_KEY": "test_openai_key",
        "NEO4J_URI": "bolt://test.neo4j.io:7687",
        "NEO4J_USERNAME": "test_neo4j_user",
        "NEO4J_PASSWORD": "test_neo4j_password",
        "LIGHTHOUSE_TOKEN": "test_lighthouse_token",
        "DESCIDB_LOG_LEVEL": "DEBUG"
    }

    # Save original values and set test values
    for var, value in test_vars.items():
        original_values[var] = os.environ.get(var)
        os.environ[var] = value

    yield test_vars

    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        else:
            if var in os.environ:
                del os.environ[var]
