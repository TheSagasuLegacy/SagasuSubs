from scrapy import Spider

from .items import BangumiSubject
from .settings import BGM_DATA_DIR


class BangumiPipeline:
    def process_item(self, item: BangumiSubject, spider: Spider):
        json_data = item.json(ensure_ascii=False, indent=4)
        storage_dir = BGM_DATA_DIR / f"{item.id}.json"
        size = storage_dir.write_text(json_data, encoding="utf-8")
        spider.logger.debug(
            f"Subject {item.name_cn or item.name!r} are stored, {size=} bytes"
        )
