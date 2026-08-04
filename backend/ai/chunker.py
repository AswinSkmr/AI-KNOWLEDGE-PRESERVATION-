"""Splits document text into overlapping chunks using recursive character splitting."""
import os
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))


@dataclass
class Chunk:
    index: int
    text: str
    char_count: int


def chunk_text(text: str) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    pieces = splitter.split_text(text)

    return [
        Chunk(index=i, text=piece, char_count=len(piece))
        for i, piece in enumerate(pieces)
        if piece.strip()
    ]