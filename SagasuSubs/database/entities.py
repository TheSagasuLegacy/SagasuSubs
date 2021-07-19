from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import declarative_base

Base = declarative_base()


class Dialogs(Base):
    __tablename__ = "dialogs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    begin = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)

    file = relationship("File", back_populates="dialogs")


class Episode(Base):
    __tablename__ = "episode"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sort = Column(Float, nullable=False)
    type = Column(Integer, nullable=False)

    series_id = Column(Integer, ForeignKey("series.id"), nullable=False, index=True)

    series = relationship("Series", back_populates="episodes")


class Series(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    episodes = relationship(Episode, back_populates="series")


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(1024), index=True, nullable=False)
    sha1 = Column(String(40), index=True, nullable=False, unique=True)
    path = Column(String, nullable=False)

    series_name = Column(String)
    series_id = Column(Integer, ForeignKey("series.id"), index=True)
    episode_name = Column(String)
    episode_id = Column(Integer, ForeignKey("episode.id"), index=True)

    dialogs = relationship(Dialogs, back_populates="file")
