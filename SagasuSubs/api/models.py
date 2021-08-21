from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DialogBase(BaseModel):
    content: str
    begin: int
    end: int
    user_id: int


class DialogCreate(DialogBase):
    file_id: str


class DialogRead(DialogBase):
    id: str
    updated: datetime
    version: int


class FileBase(BaseModel):
    filename: str
    sha1: str
    remark: Optional[str] = None
    user_id: int


class FileCreate(FileBase):
    series_id: int
    episode_id: Optional[int] = None


class FileRead(FileBase):
    id: str
    dialogs: List[DialogRead] = []
    create: datetime
