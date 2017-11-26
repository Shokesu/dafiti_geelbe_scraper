
import scrapy
import webbrowser
from ..config import global_config, Config
from tempfile import mkstemp

class Spider(scrapy.Spider):
    '''
    Clase base de GeelbeSpider y DafitiSpider
    '''
    def __init__(self, **kwargs):
        super().__init__()

        # Se pueden especificar más variables de configuración por línea de comandos,
        # o por settings de Scrapy.
        self.config = global_config.copy()
        self.config.override(Config(kwargs))

        # La configuración del scraper debe ser correcta
        self.config.check()


    def view(self, response):
        '''
        Método auxiliar muy útil para depurar. Abre el navegador web por defecto
        y muestra la respuesta a una request la cual se pasa como parámetro.
        :param response:
        :return:
        '''
        handle, path = mkstemp(suffix = '.html')
        with open(path, 'wb') as fh:
            fh.write(response.body)
        webbrowser.open(path)


    def get_config(self):
        '''
        :return: Devuelve la configuración de esta araña
        '''
        return self.config