# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from db import db, db_session
from entities.article import Article

class DefaultPipeline(object):
    def process_item(self, item, spider):
        return item



class DatabasePipeline:
    '''
    Pipeline que almacena los items scrapeados en una base de datos.
    '''
    def __init__(self):
        self.mapping_generated = False

    def open_spider(self, spider):
        if not self.mapping_generated:
            self.mapping_generated = True
            db.generate_mapping()

    def close_spider(self, spider):
        pass

    @db_session
    def process_item(self, item, spider):
        entity_types = [Article]

        try:
            entity_type = next(iter([entity_type for entity_type in entity_types if isinstance(item, entity_type.ScrapyItem)]))
            entity = entity_type.load_from_scrapy_item(item)
        except:
            pass

        return item
