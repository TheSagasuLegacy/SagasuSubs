import asyncio
from pathlib import Path
from typing import List, Optional

import httpx
import SagasuSubs.database as database
from loguru import logger
from SagasuSubs.database import dto

from . import models


class UploadFiles:
    def __init__(self, db_path: Path, base: str, upload_slice: int = 400):
        self.client = httpx.AsyncClient(base_url=base, http2=True)
        self.file_crud = database.FileCrud(db_path)
        self.dialog_crud = database.DialogCrud(db_path)
        self.upload_slice = upload_slice

    async def get_file(self, sha1: str) -> Optional[models.FileRead]:
        response = await self.client.get(f"/api/files/sha1/{sha1}")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return None
        else:
            logger.debug(f"File {sha1=} existed in database, skip.")
            return models.FileRead.parse_obj(response.json())

    async def upload_file(self, file: dto.FileRead) -> models.FileRead:
        assert file.series_id
        model = models.FileCreate(
            filename=file.filename,
            sha1=file.sha1,
            series=file.series_id,
            remark=file.path,
        )
        response = await self.client.post("/api/files", json=model.dict())
        response.raise_for_status()
        logger.debug(f"File {file.filename=}, {file.sha1=} data sync to upstream.")
        return models.FileRead.parse_obj(response.json())

    async def upload_dialogs(
        self, file_id: str, dialogs: List[dto.DialogRead], slice: int = None
    ) -> List[models.DialogRead]:
        bulk_data = [
            models.DialogCreate(
                file=file_id, content=dialog.content, begin=dialog.begin, end=dialog.end
            ).dict()
            for dialog in dialogs
        ]
        slice = slice or self.upload_slice
        responses: List[models.DialogRead] = []
        for begin in range(0, len(bulk_data), slice):
            response = await self.client.post(
                "/api/dialogs/bulk",
                timeout=30,
                json={"bulk": bulk_data[begin : begin + slice]},
            )
            response.raise_for_status()
            logger.debug(
                f"Dialog for {file_id=} data sync to upstream "
                f"({begin}-{begin+slice}, total={len(bulk_data)})."
            )
            responses.extend(map(models.DialogRead.parse_obj, response.json()))

        return responses

    async def upload_subtitles(self, file: dto.FileRead):
        try:
            if await self.get_file(file.sha1):
                return
            file_response = await self.upload_file(file)
            dialog_response = await self.upload_dialogs(file_response.id, file.dialogs)
            return dialog_response
        except Exception as e:
            logger.exception(f"Exception {e} occurred during processing file:")

    async def run(self, begin: int = 0, end: int = 0, parallel: int = 2):
        sem = asyncio.Semaphore(parallel)

        for file in self.file_crud.iterate(begin, end):
            await sem.acquire()
            task = asyncio.create_task(self.upload_subtitles(file))
            task.add_done_callback(lambda _: sem.release())
