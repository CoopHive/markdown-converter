"""
Tests for the ChromaDB client module.

This module contains tests for the VectorDatabaseManager class that manages
ChromaDB vector database collections.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from descidb.chroma_client import VectorDatabaseManager


class TestVectorDatabaseManager:
    """Test suite for VectorDatabaseManager class."""

    def test_init_with_required_components(self):
        """Test initialization with required components."""
        components = {
            "converter": ["openai"],
            "chunker": ["paragraph"],
            "embedder": ["openai"]
        }

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs') as mock_makedirs:
                # Setup mock
                mock_instance = mock_client.return_value
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Initialize the manager
                manager = VectorDatabaseManager(components=components)

                # Verify
                mock_makedirs.assert_called_once()
                assert manager.db_names == ["openai_paragraph_openai"]
                assert mock_instance.get_or_create_collection.call_count == 1

    def test_init_with_missing_components_raises_error(self):
        """Test initialization with missing components raises error."""
        # Missing 'chunker' key
        components = {
            "converter": ["openai"],
            "embedder": ["openai"]
        }

        with pytest.raises(ValueError) as excinfo:
            VectorDatabaseManager(components=components)

        assert "Components dictionary must have" in str(excinfo.value)

    def test_init_with_custom_db_path(self):
        """Test initialization with custom database path."""
        components = {
            "converter": ["openai"],
            "chunker": ["paragraph"],
            "embedder": ["openai"]
        }
        custom_path = "/tmp/test_chromadb"

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs') as mock_makedirs:
                # Setup mock
                mock_instance = mock_client.return_value
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Initialize the manager
                manager = VectorDatabaseManager(components=components, db_path=custom_path)

                # Verify
                mock_makedirs.assert_called_once_with(Path(custom_path), exist_ok=True)
                mock_client.assert_called_once_with(path=custom_path)
                assert mock_instance.get_or_create_collection.call_count == 1

    def test_initialize_databases(self):
        """Test that initialize_databases creates collections for each combination."""
        components = {
            "converter": ["openai", "markdown"],
            "chunker": ["paragraph", "fixed_length"],
            "embedder": ["openai", "huggingface"]
        }

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs'):
                # Setup mock
                mock_instance = mock_client.return_value
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Initialize the manager
                manager = VectorDatabaseManager(components=components)

                # Verify
                assert len(manager.db_names) == 8  # 2*2*2 combinations
                assert mock_instance.get_or_create_collection.call_count == 8

    def test_insert_document_valid_db(self):
        """Test inserting document into a valid database."""
        components = {
            "converter": ["openai"],
            "chunker": ["paragraph"],
            "embedder": ["openai"]
        }
        db_name = "openai_paragraph_openai"
        embedding = [0.1, 0.2, 0.3]
        metadata = {"content_cid": "test_cid", "other": "value"}
        doc_id = "test_doc_id"

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs'):
                # Setup mock
                mock_instance = mock_client.return_value
                mock_collection = MagicMock()
                mock_instance.get_collection.return_value = mock_collection
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Initialize the manager
                manager = VectorDatabaseManager(components=components)

                # Insert document
                manager.insert_document(db_name, embedding, metadata, doc_id)

                # Verify
                mock_instance.get_collection.assert_called_once_with(name=db_name)
                mock_collection.add.assert_called_once_with(
                    documents=[metadata["content_cid"]],
                    embeddings=embedding,
                    ids=[doc_id],
                    metadatas=[metadata]
                )

    def test_insert_document_invalid_db(self):
        """Test inserting document into an invalid database raises error."""
        components = {
            "converter": ["openai"],
            "chunker": ["paragraph"],
            "embedder": ["openai"]
        }
        db_name = "nonexistent_db"
        embedding = [0.1, 0.2, 0.3]
        metadata = {"content_cid": "test_cid"}
        doc_id = "test_doc_id"

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs'):
                # Setup mock
                mock_instance = mock_client.return_value
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Initialize the manager
                manager = VectorDatabaseManager(components=components)

                # Attempt to insert document into nonexistent DB
                with pytest.raises(ValueError) as excinfo:
                    manager.insert_document(db_name, embedding, metadata, doc_id)

                assert f"Database '{db_name}' does not exist" in str(excinfo.value)

    def test_print_all_metadata(self, capsys):
        """Test that print_all_metadata retrieves and prints metadata from all collections."""
        components = {
            "converter": ["openai"],
            "chunker": ["paragraph"],
            "embedder": ["openai"]
        }
        db_name = "openai_paragraph_openai"
        metadata = [{"content_cid": "test_cid", "other": "value"}]

        with patch('chromadb.PersistentClient') as mock_client:
            with patch('os.makedirs'):
                # Setup mock
                mock_instance = mock_client.return_value
                mock_collection = MagicMock()
                mock_instance.get_collection.return_value = mock_collection
                mock_instance.get_or_create_collection.return_value = MagicMock()

                # Mock collection.get() to return test metadata
                mock_collection.get.return_value = {"metadatas": metadata}

                # Initialize the manager
                manager = VectorDatabaseManager(components=components)

                # Call the method
                with patch('builtins.print') as mock_print:
                    manager.print_all_metadata()

                    # Verify print calls
                    mock_print.assert_any_call(f"\nMetadata for collection '{db_name}':")
                    mock_print.assert_any_call(metadata[0])

                # Verify collection.get() was called
                mock_collection.get.assert_called_once()
