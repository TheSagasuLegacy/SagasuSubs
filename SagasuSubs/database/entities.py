from __future__ import annotations

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Dialogs(SQLModel, table=True):
    id: int = Field(primary_key=True)
    content: str
    begin: int
    end: int

    file_id: int = Field(foreign_key="files.id", index=True)
    file: Files = Relationship(back_populates="dialogs")


class Episode(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: Optional[str] = None
    sort: float
    type: int

    series_id: int = Field(foreign_key="series.id", index=True)
    series: Series = Relationship(back_populates="episodes")


class Series(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    episodes: List[Episode] = Relationship(back_populates="series")


class Files(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=1024)
    sha1: str = Field(max_length=40)
    path: str

    series_name: str
    series_id: Optional[int] = Field(None, foreign_key="series.id", index=True)
    episode_name: str
    episode_id: Optional[int] = Field(None, foreign_key="episode.id", index=True)

    dialogs: List[Dialogs] = Relationship(back_populates="file")


Dialogs.update_forward_refs()
Episode.update_forward_refs()
Series.update_forward_refs()
Files.update_forward_refs()
