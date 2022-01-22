import scrapy


class SubjectDownloadSpider(scrapy.Spider):
    name = 'subject_download'
    allowed_domains = ['bgm.tv']
    start_urls = ['http://bgm.tv/']

    def parse(self, response):
        pass
