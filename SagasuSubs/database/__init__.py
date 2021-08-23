import abc
from pathlib import Path
from typing import Callable, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import dto, entities


class CrudBase(metaclass=abc.ABCMeta):
    def __init__(self, db_path: Path, **engine_args):
        self.db_uri = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_uri, **engine_args)
        self.session_factory: Callable[[], Session] = sessionmaker(bind=self.engine)

    @abc.abstractmethod
    def create_table(self):
        ...

    @abc.abstractmethod
    def drop_table(self):
        ...

    @abc.abstractmethod
    def create(self, model: dto.DtoModel):
        ...

    @abc.abstractmethod
    def read(self, id: int):
        ...

    @abc.abstractmethod
    def update(self, model: dto.DtoModel):
        ...

    @abc.abstractmethod
    def delete(self, id: int):
        ...


class FileCrud(CrudBase):
    def create_table(self):
        entities.File.__table__.create(bind=self.engine)

    def drop_table(self):
        entities.File.__table__.drop(bind=self.engine)

    def create(self, model: dto.FileCreate) -> dto.FileRead:  # type:ignore
        session = self.session_factory()
        with session.begin():
            entity = entities.File(**model.dict())
            session.add(entity)
            session.commit()
            session.flush()
        created = dto.FileRead.from_orm(entity)
        return created

    def read(self, id: int) -> Optional[dto.FileRead]:
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.File).get(id)
            return dto.FileRead.from_orm(entity) if entity else None

    def iterate(self, begin: int = 0, end: int = 0, size: int = 20):
        session = self.session_factory()
        with session.begin():
            for begin in range(begin, end or len(self), size):
                for entity in (
                    session.query(entities.File)
                    .order_by(entities.File.id)
                    .offset(begin)
                    .limit(size)
                ):
                    yield dto.FileRead.from_orm(entity)
        return

    def count(self, begin: int = 0, end: int = 0):
        session = self.session_factory()
        with session.begin():
            total = session.query(entities.File).count()
            return (
                session.query(entities.File)
                .offset(begin)
                .limit((end or total) - begin)
                .count()
            )

    def read_by_sha1(self, sha1: str) -> Optional[dto.FileRead]:
        session = self.session_factory()
        with session.begin():
            entity = (
                session.query(entities.File).filter(entities.File.sha1 == sha1).first()
            )
            return dto.FileRead.from_orm(entity) if entity else None

    def update(self, model: dto.FileRead) -> dto.FileRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.File(**model.dict(exclude={"dialogs"}))
            session.merge(entity)
            session.commit()
            session.flush()
        created = dto.FileRead.from_orm(entity)
        return created

    def delete(self, id: int):
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.File).get(id)
            if entity is not None:
                session.delete(entity)
            session.commit()
            session.flush()
        return

    def __iter__(self):
        return self.iterate()

    def __len__(self):
        return self.count()


class DialogCrud(CrudBase):
    """
    Crud class, same as `FileCrud`, but use `entities.Dialog`
    """

    def create_table(self):
        entities.Dialogs.__table__.create(bind=self.engine)

    def drop_table(self):
        entities.Dialogs.__table__.drop(bind=self.engine)

    def create(self, model: dto.DialogCreate) -> dto.DialogRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Dialogs(**model.dict())
            session.add(entity)
            session.commit()
            session.flush()
        created = dto.DialogRead.from_orm(entity)
        return created

    def create_bulk(self, models: List[dto.DialogCreate]):
        session = self.session_factory()
        with session.begin():
            entities_ = [entities.Dialogs(**model.dict()) for model in models]
            session.add_all(entities_)
            session.commit()
            session.flush()
        return

    def read(self, id: int) -> Optional[dto.DialogRead]:
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Dialogs).get(id)
            return dto.DialogRead.from_orm(entity) if entity else None

    def update(self, model: dto.DialogRead) -> dto.DialogRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Dialogs(**model.dict())
            session.merge(entity)
            session.commit()
            session.flush()
        created = dto.DialogRead.from_orm(entity)
        return created

    def delete(self, id: int):
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Dialogs).get(id)
            if entity is not None:
                session.delete(entity)
            session.commit()
            session.flush()
        return


class EpisodeCrud(CrudBase):
    """
    Crud class, same as `FileCrud`, but use `entities.Episode`
    """

    def create_table(self):
        entities.Episode.__table__.create(bind=self.engine)

    def drop_table(self):
        entities.Episode.__table__.drop(bind=self.engine)

    def create(self, model: dto.EpisodeCreate) -> dto.EpisodeRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Episode(**model.dict())
            session.add(entity)
            session.commit()
            session.flush()
        created = dto.EpisodeRead.from_orm(entity)
        return created

    def read(self, id: int) -> Optional[dto.EpisodeRead]:
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Episode).get(id)
            return dto.EpisodeRead.from_orm(entity) if entity else None

    def update(self, model: dto.EpisodeRead) -> dto.EpisodeRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Episode(**model.dict())
            session.merge(entity)
            session.commit()
            session.flush()
        created = dto.EpisodeRead.from_orm(entity)
        return created

    def delete(self, id: int):
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Episode).get(id)
            if entity is not None:
                session.delete(entity)
            session.commit()
            session.flush()
        return


class SeriesCrud(CrudBase):
    """
    Crud class, same as `FileCrud`, but use `entities.Series`
    """

    def create_table(self):
        entities.Series.__table__.create(bind=self.engine)

    def drop_table(self):
        entities.Series.__table__.drop(bind=self.engine)

    def create(self, model: dto.SeriesCreate) -> dto.SeriesRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Series(**model.dict())
            session.add(entity)
            session.commit()
            session.flush()
        created = dto.SeriesRead.from_orm(entity)
        return created

    def read(self, id: int) -> Optional[dto.SeriesRead]:
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Series).get(id)
            return dto.SeriesRead.from_orm(entity) if entity else None

    def update(self, model: dto.SeriesRead) -> dto.SeriesRead:
        session = self.session_factory()
        with session.begin():
            entity = entities.Series(**model.dict())
            session.merge(entity)
            session.commit()
            session.flush()
        created = dto.SeriesRead.from_orm(entity)
        return created

    def delete(self, id: int):
        session = self.session_factory()
        with session.begin():
            entity = session.query(entities.Series).get(id)
            if entity is not None:
                session.delete(entity)
            session.commit()
            session.flush()
        return
