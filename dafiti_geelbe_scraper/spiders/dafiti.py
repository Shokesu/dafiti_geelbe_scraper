import scrapy
from scrapy import Request
from .spider import Spider

class DafitiSpider(Spider):
    '''
    Araña para escrapear la página de geelbe
    '''
    name = 'dafiti'
    allowed_domains = ['https://www.dafiti.com.co/']

    def start_requests(self):
        yield Request('http://www.dafiti.com.co/', callback = self.parse)


    def parse(self, response):
        self.view(response)
