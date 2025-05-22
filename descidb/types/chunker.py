"""
Type definitions and interfaces for the chunker module.
"""

from typing import List, Literal, Callable

# Type definitions
ChunkerType = Literal["paragraph", "sentence", "word", "fixed_length"]

# Function type for all chunker implementations
ChunkerFunc = Callable[[str], List[str]]