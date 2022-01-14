from dataclasses import dataclass
from pathlib import Path

from httpx import URL


@dataclass
class DownloadItem:
    path: Path
    url: URL
