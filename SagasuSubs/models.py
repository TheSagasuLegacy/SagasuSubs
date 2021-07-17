from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from pysubs2 import SSAFile

from .utils import auto_load, sha1sum


class SubtitleFile(BaseModel):
    filename: str
    sha1: str


class DialogContent(BaseModel):
    content: str
    begin: int
    end: int


class SagasuSubtitleFile(SubtitleFile):
    filename: str
    sha1: str
    series: int
    episode: Optional[int] = None


class SagasuDialogContent(DialogContent):
    file: str


class SubtitlePersist(SubtitleFile):
    dialogs: List[DialogContent] = []
    path: Path

    @classmethod
    def from_file(cls, file: Path) -> "SubtitlePersist":
        data, sha1 = auto_load(file), sha1sum(file)
        subtitle = SSAFile.from_string(data)
        dialogs = [
            DialogContent(
                content=dialog.text,
                begin=dialog.start,
                end=dialog.end,
            )
            for dialog in subtitle.events
            if dialog.type == "Dialogue"
        ]
        return cls(filename=file.name, sha1=sha1, path=file, dialogs=dialogs)
