import scrapy
from scrapy import Request
from .spider import Spider

class GeelbeSpider(Spider):
    '''
    Araña para escrapear la página de geelbe
    '''
    name = 'geelbe'
    allowed_domains = ['http://www.geelbe.com/']

    def start_requests(self):
        yield Request('http://www.geelbe.com/', callback = self.parse)


    def parse(self, response):
        self.view(response)
