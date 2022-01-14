import httpx
from scrapy.crawler import Crawler
from scrapy.spiders import Spider
from tqdm import tqdm

from .items import DownloadItem


class FileDownloadPipeline:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(crawler)

    def process_item(self, item: DownloadItem, spider: Spider):
        with httpx.stream("GET", item.url) as response, tqdm(
            colour="green", desc=item.path.name, position=1, leave=False
        ) as progress, open(item.path, "wb") as file:
            if size := response.headers.get("Content-Length"):
                progress.total = int(size)
            for chunk in response.iter_bytes():
                progress.update(len(chunk))
                file.write(chunk)
        return item
