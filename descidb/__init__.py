"""
DeSciDB package for scientific document processing and storage.

This package provides tools for processing, chunking, embedding, and
storing scientific documents in various database systems.
"""

# Import submodules to make them available
import descidb.core
import descidb.db
import descidb.query
import descidb.rewards
import descidb.utils
from descidb.core.chunker import chunk, chunk_from_url
from descidb.core.converter import convert
from descidb.core.embedder import embed, embed_from_url

# Core functionality
from descidb.core.processor import Processor
from descidb.db.chroma_client import VectorDatabaseManager
from descidb.db.graph_db import IPFSNeo4jGraph

# Database connectors
from descidb.db.postgres_db import PostgresDBManager
from descidb.query.evaluation_agent import EvaluationAgent

# Query functionality
from descidb.query.query_db import query_collection

# Reward system
from descidb.rewards.token_rewarder import TokenRewarder
from descidb.utils.logging_utils import get_logger

# Utility functions
from descidb.utils.utils import (
    compress,
    download_from_url,
    extract,
    upload_to_lighthouse,
)

__version__ = "0.1.0"
