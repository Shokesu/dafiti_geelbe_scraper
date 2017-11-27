import scrapy
from scrapy import Request
from .spider import Spider
from logger import Logger
from scrapy.selector import Selector
from entities.article import Article

class DafitiSpider(Spider):
    '''
    Araña para escrapear la página de geelbe
    '''
    name = 'dafiti'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log = Logger(file_path = self.get_config().path.OUTPUT_DAFITI_SPIDER_LOG)
        self.log.set_level(self.get_config().LOG_LEVEL)
        self.log.output_to_stdout(True)

    def start_requests(self):
        yield self.request_brand_list()

    def request_brand_list(self):
        self.log.debug('Requesting brands list')
        request = Request(url = 'https://www.dafiti.com.co/marcas/', callback = self.parse_brand_list)
        return request

    def parse_brand_list(self, response):
        self.log.debug('Parsing brands list')

        brands = []
        for item in response.css('li.brandsLetter').extract():
            selector = Selector(text = item)
            brand, brand_url = selector.css('a::text').extract_first(), selector.css('a::attr(href)').extract_first()
            brands.append((brand, brand_url))

        self.log.debug('Extracted {} brands.', len(brands))

        for brand, brand_url in brands:
            yield self.request_brand_products_list(url = brand_url, brand = brand)



    def request_brand_products_list(self, url, brand, line = None):
        if line is None:
            self.log.debug('Requesting "{}" products', brand)
        else:
            self.log.debug('Requesting "{}" products on line "{}"', brand, line)

        callback = lambda response: self.parse_brand_products_list(response, response.meta['brand'], response.meta['line'])
        request = Request(url = url, callback = callback)
        request.meta['brand'] = brand
        request.meta['line'] = line
        return request

    def parse_brand_products_list(self, response, brand, line = None):
        if not line is None:
            self.log.debug('Parsing "{}" products list on "{}" line', brand, line)
            for item in response.css('div.itm-product-main-info').extract():
                try:
                    product = self.parse_product(selector = Selector(text = item), brand = brand, line = line)
                    yield product
                except Exception as e:
                    self.log.error(str(e))
        else:
            self.log.debug('Parsing "{}" product lines', brand)

            lines = []
            for item in response.css('div.fct-bd a'):
                line, line_url = item.css('::text').extract_first(), item.css('::attr(href)').extract_first()
                lines.append((line, line_url))

            self.log.debug('Parsed {} lines', len(lines))

            for line, line_url in lines:
                yield self.request_brand_products_list(url = line_url, brand = brand, line = line)


    def parse_product(self, selector, brand, line):
        name = selector.css('p.itm-title::text').extract_first()
        price = selector.css('span.itm-price:not(.price-prefix-listing)::text').re_first('^\D*([\d\.]+)$')
        image = None

        loader = Article.get_scrapy_item_loader()
        loader.add_value('price', price)
        loader.add_value('line', line)
        loader.add_value('name', name)
        loader.add_value('brand', brand)
        loader.add_value('provider', 'dafiti')
        loader.add_value('image', image)
        item = loader.load_item()


        self.log.debug('Extracted product info. name: {}, brand: {}, price: {}, line: {}', name, brand, price, line)

        return item