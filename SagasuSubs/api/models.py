from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DialogBase(BaseModel):
    content: str
    begin: int
    end: int


class DialogCreate(DialogBase):
    file: str


class DialogRead(DialogBase):
    id: str
    updated: datetime
    version: int


class FileBase(BaseModel):
    filename: str
    sha1: str
    remark: Optional[str] = None


class FileCreate(FileBase):
    series: int
    episode: Optional[int] = None


class FileRead(FileBase):
    id: str
    dialogs: List[DialogRead] = []
    create: datetime
