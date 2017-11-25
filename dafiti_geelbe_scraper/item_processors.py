
'''
Este script define procesadores de campos de items Scrapy.
'''

class TypeConverter:
    '''
    Es una clase de utilidad. Es un processor que puede usarse para definir los campos
    de los items. Sirver para realizar conversiones de tipo de los valores de los campos.
    Las subclases deben implementar el método convert.
    '''
    def convert(self, value):
        '''
        Modifica el tipo de un valor de entrada que se pasa como parámetro
        :param value:
        :return: Devuelve el valor de entrada con su tipo modificado.
        '''
        return value

    def __call__(self, values, loader_context = None):
        next_values = []
        for value in values:
            try:
                next_values.append(self.convert(value))
            except:
                pass
        return next_values

class ToFloat(TypeConverter):
    '''
    Sirve para formatear los campos de los items como valores flotantes
    '''
    def convert(self, value):
        return float(value)


class ToInt(TypeConverter):
    '''
    Sirve para formatear los campos de los items como valores enteros.
    '''
    def convert(self, value):
        return int(value)
