import json
from typing import Any, Dict, cast

import scrapy
from bangumi import settings
from bangumi.items import BangumiSubject
from httpx import URL
from pydantic import ValidationError
from SagasuSubs.log import logger as loguru_logger
from scrapy.http import Response
from tqdm import tqdm


def format_validation_error(e: ValidationError) -> str:
    return ", ".join(
        map(
            lambda e: "(<b>"
            + " ".join(
                map(
                    lambda k, v: f"<e>{k}</e>=<y>{v!r}</y>",
                    e.keys(),
                    e.values(),
                )
            )
            + "</b>)",
            e.errors(),
        )
    )


class SubjectDownloadSpider(scrapy.Spider):
    name = "subject_download"
    base_url = URL("https://api.bgm.tv")

    settings.BGM_DATA_DIR.mkdir(exist_ok=True, parents=True)

    def start_requests(self):
        available_offsets = [
            offset
            for offset in range(settings.BEGIN_OFFSET, settings.END_OFFSET)
            if not (settings.BGM_DATA_DIR / f"{offset}.json").is_file()
        ]
        self.logger.info(
            "Prepared %d/%d subjects to download"
            % (len(available_offsets), settings.END_OFFSET - settings.BEGIN_OFFSET)
        )
        with tqdm(available_offsets) as progress:
            for offset in progress:
                offset = cast(int, offset)
                target_url = self.base_url.copy_with(
                    path=f"/subject/{offset}", params={"responseGroup": "large"}
                )
                yield scrapy.Request(
                    url=str(target_url),
                    callback=self.parse,
                    cb_kwargs={"offset": offset},
                )
        return

    def parse(self, response: Response, *, offset: int):
        data: Dict[str, Any] = json.loads(response.body)
        if "id" not in data:
            code, message = data.get("code"), data.get("error")
            self.logger.warning(f"Request Bangumi failed, {offset=} {code=} {message=}")
            return

        try:
            subject = BangumiSubject.parse_obj(data)
        except ValidationError as e:
            loguru_logger.opt(colors=True).error(
                f"ValidationError: {format_validation_error(e)}"
            )
            return

        if subject.id != offset:
            self.logger.warning(f"Subject id mismatch: {subject.id=} {offset=}")
            return

        yield subject
