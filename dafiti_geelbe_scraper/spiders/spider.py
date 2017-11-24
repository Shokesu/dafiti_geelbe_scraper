
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

        # La configuración del scraper debe ser correcta
        global_config.check()


        # La araña puede tener configuración adicional
        # Puede ser especificada via settings en scrapy o por linea
        # de comandos.
        self.config = Config(kwargs)


    def get_config(self):
        '''
        :return: Devuelve la configuración de la araña
        '''
        return self.config



    def view(self, response):
        '''
        Método auxiliar muy útil para depurar. Abre el navegador web por defecto
        y muestra la respuesta a una request la cual se pasa como parámetro.
        :param response:
        :return:
        '''
        handle, path = mkstemp()
        with open(path, 'wb') as fh:
            fh.write(response.body)
        webbrowser.open(path)
