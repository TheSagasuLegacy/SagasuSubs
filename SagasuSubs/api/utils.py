from functools import lru_cache
from typing import List, Optional

import httpx
from SagasuSubs.database import dto


class NotebookAPIUtils:
    def __init__(self, base: str):
        self.client = httpx.Client(http2=True, base_url=base)

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
        response = self.client.get(f"api/series/{series_id}")
        response.raise_for_status()
        data = response.json()
        return [
            dto.EpisodeCreate.parse_obj({**episode, "series_id": series_id})
            for episode in data["episodes"]
        ]
