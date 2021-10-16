# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.spiders import Spider


class RandomUserAgentMiddleware:
    def __init__(self, settings: Settings):
        self.user_agent = settings.get("USER_AGENT", "Scrapy")
        self.user_agent_list = settings.getlist("USER_AGENT_LIST", [])

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        instance = cls(crawler.settings)
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        return instance

    def spider_opened(self, spider: Spider):
        if self.user_agent_list:
            spider.logger.info(f"{len(self.user_agent_list)} user agents loaded")
        self.user_agent = getattr(spider, "user_agent", None) or (
            random.choice(self.user_agent_list)
            if self.user_agent_list
            else self.user_agent
        )

    def process_request(self, request: Request, spider: Spider):
        if self.user_agent:
            request.headers.setdefault("User-Agent", self.user_agent)
        return
