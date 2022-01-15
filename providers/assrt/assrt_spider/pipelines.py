from time import sleep

import aria2p
import aria2p.client
from scrapy.crawler import Crawler
from scrapy.spiders import Spider

from .items import DownloadItem


class FileDownloadPipeline:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        port: int = self.crawler.settings.getint(
            "ARIA2_PORT", aria2p.client.DEFAULT_PORT
        )
        host: str = self.crawler.settings.get(
            "ARIA2_HOST", aria2p.client.DEFAULT_HOST
        )  # type:ignore
        secret: str = self.crawler.settings.get("ARIA2_SECRET", "")  # type:ignore
        timeout: int = self.crawler.settings.getint(
            "ARIA2_TIMEOUT", aria2p.client.DEFAULT_TIMEOUT
        )

        self.api = aria2p.API(
            aria2p.Client(host=host, port=port, secret=secret, timeout=timeout)
        )
        self.check_interval: int = self.crawler.settings.getint(
            "ARIA2_CHECK_INTERVAL", 0.5
        )

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(crawler)

    def open_spider(self, spider: Spider):
        stats = self.api.get_stats()
        spider.logger.info(
            "Aria2c stats: "
            f"{stats.num_stopped_total=}, {stats.num_active=}, {stats.num_waiting=}"
        )

    def process_item(self, item: DownloadItem, spider: Spider):
        download, *_ = self.api.add(
            uri=str(item.url),
            options=aria2p.Options(
                api=self.api,
                struct={"dir": str(item.path.parent), "out": item.path.name},
            ),
        )
        spider.logger.debug(
            f"Aria2c download hans been scheduled: {download.gid=}, {download.status=}"
        )
        while download.is_waiting:
            sleep(self.check_interval)
            download.update()
        spider.logger.debug(
            f"Aria2c download has started: {download.gid=}, {download.download_speed=}"
        )
        return item
