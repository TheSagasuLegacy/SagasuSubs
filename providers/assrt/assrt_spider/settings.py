# flake8:noqa:E501
from pathlib import Path

import scrapy.utils.log
from SagasuSubs.log import LoguruHandler

scrapy.utils.log._get_handler = lambda *_, **__: LoguruHandler(LOG_LEVEL)

# Scrapy settings for assrt_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "assrt_spider"

SPIDER_MODULES = ["assrt_spider.spiders"]
NEWSPIDER_MODULE = "assrt_spider.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'assrt_spider.middlewares.AssrtSpiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "assrt_spider.middlewares.RandomUserAgentMiddleware": 300,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 543,
    "scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'assrt_spider.pipelines.AssrtSpiderPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_LEVEL = "INFO"

DOWNLOAD_TIMEOUT = 12

RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = range(210, 1000)
RETRY_PRIORITY_ADJUST = 2

CURRENT_DIR = Path(__file__).parent.absolute()
BGM_DATA_DIR = CURRENT_DIR.parent / "data"
DOWNLOAD_DIR = CURRENT_DIR.parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
assert BGM_DATA_DIR.is_dir()

USER_AGENT_LIST = [
    stripped_line
    for line in (
        (CURRENT_DIR / "user-agents.txt")
        .read_text(encoding="utf-8")
        .splitlines(keepends=False)
    )
    if (stripped_line := line.strip()) and not line.startswith("#")
]
