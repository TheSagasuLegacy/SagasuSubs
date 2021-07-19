import hashlib
import os
from pathlib import Path
from typing import Iterator, Optional

import cchardet


def sha1sum(file: Path) -> str:
    """
    Calculate the sha1 hash of a file.
    """
    return hashlib.sha1(file.read_bytes()).hexdigest()


def detect_encoding(file: Path) -> Optional[str]:
    """
    Detect file encoding using cchardet
    """
    with file.open("rb") as f:
        return cchardet.detect(f.read())["encoding"]


def iterate_files(directory: Path, ext: str = None) -> Iterator[Path]:
    """
    Walk path and return file paths with specified extension name.
    """
    for dir, folders, files in os.walk(directory):
        for file in files:
            if ext and not file.endswith(ext):
                continue
            yield Path(dir) / file
    return


def auto_load(file: Path) -> str:
    """
    Load file using cchardet and automatically detect encoding.
    """
    with file.open(
        "r", encoding=detect_encoding(file) or "utf-8", errors="ignore"
    ) as f:
        return f.read()
