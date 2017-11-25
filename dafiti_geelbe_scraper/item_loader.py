
from scrapy.loader import ItemLoader as ScrapyItemLoader

class ItemLoader(ScrapyItemLoader):
    '''
    Esta clase es un wrapper sobre la clase ItemLoader de scrapy.
    Tiene una funcionalidad añadida: Comprueba al calcular finalmente los valores de
    los campos del item, si están presentes o no. Si algún campo no está presente y se ha
    marcado como obligatorio, se genera una excepción al cargar el item (de tipo ValueError)
    Los campos pueden marcarse como obligatorios pasandoles el atributo "mandatory" a True en
    la declaración del mismo (clase Item)
    '''
    def __init__(self, *args, **kwargs):
        '''
        Inicializa la instancia.
        :param args:
        :param kwargs:
        '''
        super().__init__(*args, **kwargs)


    def load_item(self):
        item = super().load_item()

        for field_name in item.fields:
            field = item.fields[field_name]
            if 'mandatory' in field and field['mandatory']:
                if item.get(field_name) is None:
                    raise ValueError('Missing attribute "{}" on item'.format(field_name))
        return item