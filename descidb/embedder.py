"""
Text embedding module for DeSciDB.

This module provides functions for creating vector embeddings from text chunks
using various embedding models like OpenAI's embedding API.
"""

import os
from typing import List, Literal

from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModel

from descidb.utils import download_from_url

load_dotenv(override=True)

EmbederType = Literal["openai", "nvidia"]


def embed_from_url(embeder_type: EmbederType, input_url: str) -> List[str]:
    """Embed based on the specified embedding type."""
    donwload_path = download_from_url(url=input_url)

    with open(donwload_path, "r") as file:
        input_text = file.read()

    return embed(embeder_type=embeder_type, input_text=input_text)


def embed(embeder_type: EmbederType, input_text: str) -> List[str]:
    """Chunk based on the specified chunking type."""

    chunking_methods = {"openai": openai, "nvidia": nvidia}

    return chunking_methods[embeder_type](text=input_text)


def openai(text: str) -> list:
    """Embed text using the OpenAI embedding API. Returns a list."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(model="text-embedding-3-small", input=[text])
    embedding = response.data[0].embedding
    return embedding


def nvidia(text: str) -> list:
    pass
