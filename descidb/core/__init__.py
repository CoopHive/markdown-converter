"""
Core functionality for document processing.

This module provides classes and functions for converting, chunking, embedding,
and processing documents.
"""

from descidb.core.chunker import (
    chunk,
    chunk_from_url,
    fixed_length,
    paragraph,
    sentence,
    word,
)
from descidb.core.converter import convert, convert_from_url
from descidb.core.embedder import embed, embed_from_url, openai_embed
from descidb.core.processor import Processor
