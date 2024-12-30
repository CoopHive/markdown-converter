import re
from typing import List, Literal

from descidb.utils import download_from_url

ChunkerType = Literal["paragraph", "sentence", "word"]


def chunk_from_url(chunker_type: ChunkerType, input_url: str) -> List[str]:
    """Chunk based on the specified chunking type."""
    donwload_path = download_from_url(url=input_url)

    with open(donwload_path, "r") as file:
        input_text = file.read()

    return chunk(chunker_type=chunker_type, input_text=input_text)


def chunk(chunker_type: ChunkerType, input_text: str) -> List[str]:
    """Chunk based on the specified chunking type."""

    # Mapping chunking types to functions
    chunking_methods = {"paragraph": paragraph,
                        "sentence": sentence, "word": word}

    return chunking_methods[chunker_type](text=input_text)


def paragraph(text: str) -> List[str]:
    """Chunk the text by paragraphs."""
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]


def sentence(text: str) -> List[str]:
    """Chunk the text by sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def word(text: str) -> List[str]:
    """Chunk the text by words."""
    words = text.split()
    return [w.strip() for w in words if w.strip()]
