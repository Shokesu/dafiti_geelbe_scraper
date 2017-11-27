
'''
Este script define procesadores de campos de items Scrapy.
'''

from re import match, sub

class ValueConverter:
    '''
    Es una clase de utilidad. Es un processor que puede usarse para definir los campos
    de los items. Sirver para realizar conversiones de los valores de los campos.
    '''
    def convert(self, value):
        '''
        Modifica un valor de entrada que se pasa como parámetro
        :param value:
        :return: Devuelve un valor modificado.
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

class ToFloat(ValueConverter):
    '''
    Sirve para formatear los campos de los items como valores flotantes
    '''
    def convert(self, value):
        return float(value)


class ToInt(ValueConverter):
    '''
    Sirve para formatear los campos de los items como valores enteros.
    '''
    def convert(self, value):
        return int(value)


class NameFormatter(ValueConverter):
    '''
    Sirve para formatear los campos de los items como nombres propios.
    Las palabras se separarán por un único espacio (el resto de espacios
    se eliminan)
    Las primera palabra comenzará con una mayúscula. El resto serán minúsculas
    '''
    def convert(self, value):
        name = str(value)
        name = match('^[ ]*(.*[^ ])[ ]*$', name).group(1)
        name = sub('[ ]+', ' ', name)
        name = name[0].upper() + name[1:].lower()
        return name