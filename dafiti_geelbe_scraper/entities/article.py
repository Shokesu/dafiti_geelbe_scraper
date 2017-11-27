
from .entity import Entity, EntityMixins
from pony.orm import PrimaryKey, Required, Optional, composite_key
import scrapy
from item_processors import *
from scrapy.loader.processors import TakeFirst

class Article(Entity, EntityMixins):
    '''
    Representa la entidad Artículo.
    '''

    # Definición de atributos de la entidad (Base de datos)
    id = PrimaryKey(int, auto=True)
    price = Required(float)
    name = Required(str)
    line = Required(str)
    brand = Required(str)
    provider = Required(str)
    image = Optional(str)
    composite_key(name, provider)


    # Definición de los atributos de la entidad (Scrapy)
    class ScrapyItem(scrapy.Item):
        price = scrapy.Field(input_processor = ToFloat(), output_processor = TakeFirst(), mandatory = True)
        name = scrapy.Field(output_processor = TakeFirst(), mandatory = True)
        line = scrapy.Field(input_processor = NameFormatter(), output_processor = TakeFirst(), mandatory = True)
        brand = scrapy.Field(input_processor = NameFormatter(), output_processor = TakeFirst(), mandatory = True)
        provider = scrapy.Field(output_processor = TakeFirst(), mandatory = True)
        image = scrapy.Field(output_processor = TakeFirst(), mandatory = False)


