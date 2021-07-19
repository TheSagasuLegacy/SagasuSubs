import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from pysubs2 import SSAFile

from .utils import auto_load, sha1sum

FX_REGEX = re.compile(r"\{(?:\\.+?)*?\}")


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
    def from_file(
        cls,
        file: Path,
        format: str = None,
        exclude_fx: bool = False,
        min_length: int = 3,
    ) -> "SubtitlePersist":
        data, sha1 = auto_load(file), sha1sum(file)
        subtitle = SSAFile.from_string(data, format)
        result = cls(filename=file.name, sha1=sha1, path=file)
        for dialog in subtitle.events:
            if dialog.type != "Dialogue":
                continue
            content = (
                (FX_REGEX.sub("", dialog.text) if exclude_fx else dialog.text)
                .strip()
                .replace(r"\\N", "\n")
                .replace(r"\\R", "\r")
            )
            if len(content) < min_length:
                continue
            result.dialogs.append(
                DialogContent(
                    content=content,
                    begin=dialog.start,
                    end=dialog.end,
                )
            )
        result.dialogs.sort(key=lambda dialog: dialog.begin)
        return result
