from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from SagasuSubs.database.dto import EpisodeCreate, SeriesCreate


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


class EpisodeRead(BaseModel):
    id: int
    series_id: int
    name: Optional[str] = None
    sort: Optional[float]
    type: Optional[int]
    name_cn: Optional[str] = None


class SeriesRead(BaseModel):
    id: int
    name: str
    name_cn: Optional[str] = None
    description: Optional[str] = None
    air_date: Optional[datetime] = None
    bangumi_id: Optional[int] = None
    episodes: List[EpisodeRead] = []

    def to_dto(self):
        return (
            SeriesCreate.parse_obj(self.dict()),
            [EpisodeCreate.parse_obj(model.dict()) for model in self.episodes],
        )


class ManyReadMeta(BaseModel):
    itemCount: int
    itemsPerPage: int
    totalPages: int
    totalItems: int
    currentPage: int


class ManySeriesGet(BaseModel):
    items: List[SeriesRead] = []
    meta: ManyReadMeta
