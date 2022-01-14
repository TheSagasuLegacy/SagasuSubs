import json
import os
import random
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import urljoin
from uuid import uuid4

import scrapy
from assrt_spider import settings
from httpx import URL
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.http import Request, TextResponse
from scrapy.selector import Selector
from tqdm import tqdm


def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


class SearchResult(TypedDict):
    title: str
    url: str
    similarity: float


class AssrtSearchSpider(scrapy.Spider):
    name = "assrt_search"
    target_urls = ["http://2.assrt.net", "http://assrt.net"]
    download_dir = settings.DOWNLOAD_DIR / "list"

    download_dir.mkdir(exist_ok=True, parents=True)

    @property
    def root_url(self) -> str:
        return random.choice(self.target_urls)

    def start_requests(self):
        data_files = [
            settings.BGM_DATA_DIR / file
            for file in os.listdir(settings.BGM_DATA_DIR)
            if file.endswith(".json")
        ]
        opened_ids = set()
        data_files.sort(key=lambda x: x.stat().st_atime)
        with tqdm(data_files) as progress:
            for i, data_file in enumerate(progress):
                data_file: Path
                submitted = len(opened_ids)
                skipped = (i - len(opened_ids)) / (i + 1)
                progress.set_description(f"{submitted=}, {skipped=:.3%}")

                with open(data_file, "rt", encoding="utf-8") as f:
                    data: Dict[str, Any] = json.load(f)
                type, id = data.get("type"), data.get("id")
                name = data.get("name_cn") or data.get("name")

                if type != 2:
                    continue
                if (name or id) is None:
                    self.logger.warning(f"{data_file=} has no name or id field, skip.")
                    continue
                if id in opened_ids:
                    self.logger.debug(f"{name=} has been opened, skip.")
                    continue
                if (self.download_dir / f"{id}.json").is_file():
                    self.logger.debug(f"{name=} has been downloaded, skip.")
                    continue

                url = URL(
                    self.root_url,
                    path="/sub/",
                    params={
                        "searchword": name,
                        "page": 1,
                        "sort": "relevance",
                        "no_muxer": 1,
                    },
                )
                yield Request(
                    url=str(url),
                    callback=self.parse,
                    cb_kwargs={"name": name, "id": id},
                    cookies={"u3": uuid4().hex},
                )
                opened_ids.add(id)
        return

    def parse(self, response: TextResponse, *, name: str, id: int):
        if result_count := response.selector.css("#result-count").get():
            self.logger.debug(f"Search page {result_count=}")
        else:
            return get_retry_request(
                response.request, spider=self, reason="blank page returned"
            )
        download_subjects: List[Selector] = [*response.selector.css(".introtitle")]
        subject_data: List[SearchResult] = []
        for subject in download_subjects:
            title: Optional[str] = subject.attrib.get("title")
            path: Optional[str] = subject.attrib.get("href")
            if (title is None) or (path is None):
                continue
            subject_data.append(
                {
                    "title": title,
                    "url": urljoin(self.root_url, path),
                    "similarity": text_similarity(title, name),
                }
            )
        subject_data.sort(key=lambda x: x["similarity"], reverse=True)
        if not subject_data:
            self.logger.debug(f"Result for {name=} has no avaliable subject, skip.")
            return
        data = {"name": name, "id": id, "subjects": subject_data}
        data_path = self.download_dir / f"{id}.json"
        if data_path.is_file():
            self.logger.debug(f"Subject {name=} {data_path=} already exists, skip.")
            return
        with open(data_path, "wt", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Subject {id=} {name=} downloaded.")
