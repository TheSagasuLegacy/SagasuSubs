import json
import os
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, cast
from urllib.parse import unquote_plus
from uuid import uuid4

import scrapy
from assrt_spider import settings
from httpx import URL
from scrapy import Request
from scrapy.http import TextResponse
from scrapy.selector import Selector
from tqdm import tqdm

if TYPE_CHECKING:
    from assrt_spider.spiders.assrt_search import SearchResult

from assrt_spider.items import DownloadItem


class SearchList(TypedDict):
    name: str
    id: str
    subjects: List["SearchResult"]


class AssrtDownloadSpider(scrapy.Spider):
    name = "assrt_download"
    target_urls = [
        "https://assrt.net",
        "https://2.assrt.net",
    ]
    download_dir = settings.DOWNLOAD_DIR / "subtitle"
    subject_lists_dir = settings.DOWNLOAD_DIR / "list"

    download_dir.mkdir(exist_ok=True, parents=True)

    @property
    def root_url(self) -> str:
        return random.choice(self.target_urls)

    def start_requests(self):
        subject_map = {
            search_list_path: subject_data_path
            for file in os.listdir(self.subject_lists_dir)
            if (search_list_path := self.subject_lists_dir / file).is_file()
            and (subject_data_path := settings.BGM_DATA_DIR / file).is_file()
        }

        with tqdm(iterable=subject_map.items(), position=0) as progress:
            for search_list_path, subject_data_path in progress:
                search_list_path: Path
                subject_data_path: Path

                with open(search_list_path, "rt", encoding="utf-8") as list_file, open(
                    subject_data_path, "rt", encoding="utf-8"
                ) as data_file:
                    search_list: SearchList = json.load(list_file)
                    subject_data = json.load(data_file)

                name, id = search_list["name"], search_list["id"]

                progress.set_description(f"{id=}, {name=}")

                subjects = [
                    subject
                    for subject in sorted(
                        search_list["subjects"],
                        key=lambda x: x["similarity"],
                        reverse=True,
                    )
                    if subject["similarity"] >= 0.1
                ]

                if not subjects:
                    self.logger.debug(
                        f"{id=} {name=} has no subjects with enough similarity."
                    )
                    continue

                for subject in subjects:
                    origin_url = URL(subject["url"])
                    new_url = URL(
                        self.root_url, path=origin_url.path, params={"searchword": name}
                    )
                    yield Request(
                        url=str(new_url),
                        callback=self.parse,
                        cb_kwargs={
                            "name": name,
                            "id": id,
                            "search_data": subject,
                            "subject_data": subject_data,
                        },
                        cookies={"u3": uuid4().hex},
                    )

        return

    def parse(
        self,
        response: TextResponse,
        *,
        name: str,
        id: int,
        search_data: "SearchResult",
        subject_data: Dict[str, Any],
    ):
        main_title: Optional[str] = response.selector.css(".name_org").get()
        detail_html = response.selector.css("#detail-tbl-main > div > div")
        download_btn = response.selector.css("#btn_download")

        if (
            (main_title is None)
            or (detail_html.getall() is None)
            or (download_btn.get() is None)
            or ((download_url_path := download_btn.attrib.get("href")) is None)
        ):
            self.logger.warning(f"{id=} {name=} failed to parse result page")
            return

        download_url = URL(self.root_url, path=unquote_plus(download_url_path))
        filename = os.path.basename(download_url.path)
        basefilename, _ = os.path.splitext(filename)

        details_text = ""
        for detail_line in detail_html:
            detail_line, detail_line_text = cast(Selector, detail_line), ""
            for detail_span in detail_line.css("span[class^=subdes], span[class^=col]"):
                detail_span = cast(Selector, detail_span)
                detail_span_text: Optional[str] = detail_span.css("::text").get()
                if (detail_span_text is not None) and (
                    detail_span_text := detail_span_text.strip()
                ):
                    detail_line_text += detail_span_text + "\t"
            details_text += detail_line_text.strip() + "\n"
        details_text = details_text.strip()

        save_dir = self.download_dir / str(id)
        save_dir.mkdir(exist_ok=True, parents=True)
        download_dir = save_dir / "downloads"
        download_dir.mkdir(exist_ok=True, parents=True)

        with open(save_dir / "subject.json", "wt", encoding="utf-8") as f:
            json.dump(subject_data, f, ensure_ascii=False, indent=4)

        with open(download_dir / (basefilename + ".txt"), "wt", encoding="utf-8") as f:
            f.write(details_text)

        if (download_path := download_dir / filename).is_file():
            return

        yield DownloadItem(path=download_path, url=download_url)
