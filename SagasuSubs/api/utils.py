from functools import lru_cache
from typing import List, Optional

import httpx
from SagasuSubs.database import dto

from .auth import AuthTokenManager
from .models import ManySeriesGet


class NotebookAPIUtils:
    def __init__(self, base: str):
        self.auth_info = AuthTokenManager.get_token()
        self.client = httpx.Client(
            http2=True,
            base_url=base,
            headers={"Authorization": "Bearer " + self.auth_info.token},
        )

    @lru_cache(maxsize=16)
    def search(self, keyword: str) -> Optional[dto.SeriesCreate]:
        response = self.client.get(
            "/api/series/search",
            params={"keyword": keyword, "fields": ["name", "name_cn", "description"]},
        )
        response.raise_for_status()
        data = response.json()
        return next(
            (
                dto.SeriesCreate(id=result["info"]["id"], name=result["info"]["name"])
                for result in data["results"]
            ),
            None,
        )

    @lru_cache(maxsize=16)
    def episodes(self, series_id: int) -> List[dto.EpisodeCreate]:
        response = self.client.get(f"/api/series/{series_id}")
        response.raise_for_status()
        data = response.json()
        return [
            dto.EpisodeCreate.parse_obj({**episode, "series_id": series_id})
            for episode in data["episodes"]
        ]

    def iterate_series(self, begin: int = 1, size: int = 50):
        while True:
            response = self.client.get(
                "/api/series", params={"limit": size, "page": begin, "join": "episodes"}
            )
            response.raise_for_status()
            model = ManySeriesGet.parse_obj(response.json())
            yield model
            if begin >= model.meta.totalPages:
                break
            begin += 1
        return
