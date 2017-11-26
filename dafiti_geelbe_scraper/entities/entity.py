


from item_loader import ItemLoader
from db import db


class EntityMixins:
    @classmethod
    def get_scrapy_item_loader(cls, **kwargs):
        '''
        Devuelve una instancia de la clase ItemLoader con la que puede generarse un nuevo
        item de scrapy de esta entidad.
        e.g:
        loader = Article.get_scrapy_item_loader()
        loader.add_value('price', 500)
        item = loader.load_item()
        :return:
        '''
        return ItemLoader(item = cls.ScrapyItem(), **kwargs)


    @classmethod
    def load_from_scrapy_item(cls, item):
        '''
        Convierte un item de la librería Scrapy asociado a esta entidad, a un objeto de la libería
        Pony, la cual facilita hacer ORM sobre una base de datos con los campos de la entidad.

        :param item:
        :return: Devuelve un objeto de la librería Pony con el que puede hacerse ORM
        '''

        fields = dict([(key, item[key]) for key in item])
        entity = cls(**fields)
        return entity

Entity = db.Entity