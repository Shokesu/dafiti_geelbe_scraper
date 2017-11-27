import scrapy
from scrapy import Request
from .spider import Spider
from splash_utils import splash_request
from entities.article import Article

from logger import Logger
from config import global_config


from urllib.parse import urlencode
import re

class GeelbeSpider(Spider):
    '''
    Araña para escrapear la página de geelbe
    '''
    name = 'geelbe'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log = Logger(file_path = global_config.path.OUTPUT_GEELBE_SPIDER_LOG)
        self.log.set_level(self.get_config().LOG_LEVEL)
        self.log.output_to_stdout()

    def start_requests(self):
        # Scrapeamos productos de la línea 'Mujeres'
        yield self.request_products_list(line = 'woman')

        # Scrapeamos productos de la línea 'Hombres'
        yield self.request_products_list(line = 'man')

        # Scrapeamos productos de la línea 'Niños'
        yield self.request_products_list(line = 'child')


    def request_products_list(self, line, page = 1):
        lineIDs = {
            'woman' : 639,
            'man' : 590,
            'child' : 693
        }
        params = {
            'page' : page,
            'pagesToLoad' : 1,
            'categoryId' : lineIDs[line],
            'filters' : '[]',
            'attributes' : '[]',
            'features' : '[]',
            'warehouseId' : '[]',
            'providerId' : '[]',
            'warehouses' : '[]'
        }
        params = dict([(key, str(value)) for key, value in params.items()])
        url = 'http://www.geelbe.com/ajax/lazyLoad.php?{}'.format(urlencode(params))

        callback = lambda response: self.parse_products_list(response, response.meta['line'], response.meta['page'])

        self.log.debug('Requesting products list on Geelbe. Line: {}, page: {}', line, page)
        request = Request(url = url, callback = callback)
        request.meta['line'], request.meta['page'] = line, page
        return request


    def parse_products_list(self, response, line, page):
        product_urls = response.css('.analyticsProduct a::attr(href)').extract()
        if len(product_urls) > 0:
            self.log.debug('Parsing products list. Line: {}, page: {}. Number of products: {}', line, page, len(product_urls))

            for product_url in product_urls:
                yield self.request_product(url = product_url, line = line)

            # Pedir la siguiente página
            yield self.request_products_list(line = line, page = page + 1)



    def request_product(self, url, line):
        callback = lambda response:self.parse_product(response, response.meta['line'])
        request = Request(url = url, callback = callback)
        request.meta['line'] = line
        return request


    def parse_product(self, response, line):
        try:
            description =  '\n'.join(response.xpath('//div[@itemprop = "description"]/node()').extract())
            name = response.xpath('//h1[@itemprop = "name"]/text()').extract_first()
            price = response.xpath('//span[@itemprop = "price"]/text()').extract_first()
            image = response.css('.fotos > img::attr(src)').extract_first()
            category = None

            self.log.debug('Parsing product with name: "{}"', name)

            search = lambda pattern, string: re.search(pattern, string, re.DOTALL)
            match = lambda pattern, string: re.match(pattern, string, re.DOTALL)


            def product_property(property):
                value = search('<b>{}</b>([^<]+)<br>'.format(property), description).group(1)
                value = match('^\s*:\s*([ \w]+)\s*$', value).group(1)
                value = match('^[ ]*([ \w]*\w)[ ]*$', value).group(1)
                return value

            brand = product_property('Marca')
            line = product_property('L.nea')

            self.log.debug('Info extracted. Price: {}, Brand: {}', price, brand)


            loader = Article.get_scrapy_item_loader()
            loader.add_value('price', price)
            loader.add_value('line', line)
            loader.add_value('name', name)
            loader.add_value('brand', brand)
            loader.add_value('provider', 'geelbe')
            loader.add_value('image', image)
            item = loader.load_item()

            yield item

        except Exception as e:
            self.log.error('Failed extracting data: {}', e)