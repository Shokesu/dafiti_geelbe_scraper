
from .entity import Entity
from pony.orm import PrimaryKey, Required
import scrapy
from item_processors import *
from scrapy.loader.processors import TakeFirst

class Article(*Entity):
    '''
    Representa la entidad Artículo.
    '''

    # Nombre alternativo para la tabla de la entidad en la base de datos
    _table = 'article'

    # Definición de atributos de la entidad (Base de datos)
    id = PrimaryKey(int, auto=True)
    price = Required(float)
    category = Required(str)
    name = Required(str, unique=True)
    line = Required(str)
    brand = Required(str)


    # Definición de los atributos de la entidad (Scrapy)
    class ScrapyItem(scrapy.Item):
        price = scrapy.Field(input_processor = ToFloat(), output_processor = TakeFirst(), mandatory = True)
        category = scrapy.Field(output_processor = TakeFirst(), mandatory = True)
        name = scrapy.Field(output_processor = TakeFirst(), mandatory = True)
        line = scrapy.Field(output_processor = TakeFirst(), mandatory = True)
        brand = scrapy.Field(output_processor = TakeFirst(), mandatory = True)



