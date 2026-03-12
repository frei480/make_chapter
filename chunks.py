import os
from pathlib import Path

import tiktoken
from tiktoken.core import Encoding

from config import cfg

os.environ["TIKTOKEN_CACHE_DIR"] = cfg.main.TIKTOKEN_CACHE_DIR


def count_tokens(text: str, encoding: Encoding) -> int:
    return len(encoding.encode(text))


def get_chunks(file: Path, max_tokens_per_request: int) -> list[list[str]]:
    encoding = tiktoken.get_encoding("cl100k_base")

    content = file.read_text(encoding="utf-8")

    parts = content.split("\n\n")
    tokens = 0
    chunk: list[str] = []
    chunks: list[list[str]] = []
    for part in parts:
        current_tokens = count_tokens(part, encoding)
        if (tokens + current_tokens) < max_tokens_per_request:
            tokens += current_tokens
            chunk.append(part)
        else:
            chunks.append(chunk)
            chunk = []
            tokens = 0

    return chunks if chunks else [chunk]


if __name__ == "__main__":
    get_chunks(Path(__file__), 1000)
