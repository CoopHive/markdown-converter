import re
from typing import List


class Chunker:
    def paragraph(self, text: str) -> List[str]:
        """Chunk the text by paragraphs."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    def sentence(self, text: str) -> List[str]:
        """Chunk the text by sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def word(self, text: str) -> List[str]:
        """Chunk the text by words."""
        words = text.split()
        return [w.strip() for w in words if w.strip()]
