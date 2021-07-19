from typing import List, Optional

from pydantic import BaseModel


class DtoModel(BaseModel):
    class Config:
        orm_mode = True


class DialogCreate(DtoModel):
    content: str
    begin: int
    end: int
    file_id: int


class DialogRead(DialogCreate):
    id: int


class FileCreate(DtoModel):
    filename: str
    sha1: str
    path: str

    series_name: Optional[str] = None
    series_id: Optional[int] = None
    episode_name: Optional[str] = None
    episode_id: Optional[int] = None


class FileRead(FileCreate):
    id: int
    dialogs: List[DialogRead]


class EpisodeCreate(DtoModel):
    id: int
    name: Optional[str] = None
    sort: float
    type: int
    series_id: int


class EpisodeRead(EpisodeCreate):
    pass


class SeriesCreate(DtoModel):
    id: int
    name: str


class SeriesRead(SeriesCreate):
    episodes: List[EpisodeRead]
