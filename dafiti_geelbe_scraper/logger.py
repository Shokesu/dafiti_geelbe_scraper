

from config import global_config

class Logger:
    '''
    Esta clase permite imprimir mensajes a un fichero de log y/o a la salida estandard.

    Al inicializar, se lee la variable de configuración global LOG_LEVEL. Se establecerá el nivel
    de este logger como se indique en dicha variable. Puedes cambiar posteriormente el nivel
    con el método set_level

    También se comprobará la variable global OUTPUT_LOG_TO_STDOUT. En el caso de que esté a True,
    se mostrarán los mensajes de logs generados por stdout.
    '''

    def __init__(self, file_path = None):
        self.severity = {
            'info' : 1,
            'debug' : 2,
            'warning' : 3,
            'error' : 4
        }
        self.file_path = file_path

        if not self.file_path is None:
            try:
                with open(self.file_path, 'wb') as fh:
                    pass
            except:
                pass

        self.level = 'debug'
        if global_config.is_set('LOG_LEVEL'):
            self.set_level(global_config.LOG_LEVEL)


    def message(self, level, message, *args):
        if self.severity[level] < self.severity[self.level]:
            return

        message = '{}: {}'.format(level.upper(), message.format(*args))

        if global_config.is_true('OUTPUT_LOGS_TO_STDOUT'):
            print(message)

        if not self.file_path is None:
            try:
                with open(self.file_path, 'a') as fh:
                    print(message, file = fh)
            except:
                pass

    def info(self, message, *args):
        '''
        Imprime un mensaje de información en el log.
        :param message: Es el mensaje. Puede contener placeholders como los que se usan en string.format.
        :param args: Son argumentos para rellenar los placeholders, como en string.format
        '''
        self.message('info', message , *args)

    def warning(self, message, *args):
        '''
        Imprime un mensaje de warning en el log.
        :param message: Es el mensaje. Puede contener placeholders como los que se usan en string.format.
        :param args: Son argumentos para rellenar los placeholders, como en string.format
        '''
        self.message('warning', message, *args)

    def debug(self, message, *args):
        '''
        Imprime un mensaje de depuración en el log.
        :param message: Es el mensaje. Puede contener placeholders como los que se usan en string.format.
        :param args: Son argumentos para rellenar los placeholders, como en string.format
        '''
        self.message('debug', message, *args)

    def error(self, message, *args):
        '''
        Imprime un mensaje de error en el log.
        :param message: Es el mensaje. Puede contener placeholders como los que se usan en string.format.
        :param args: Son argumentos para rellenar los placeholders, como en string.format
        '''
        self.message('error', message, *args)


    def set_level(self, level = None):
        '''
        Establece el nivel de este logger. Los mensajes en un nivel menos severo al especificado serán ignorados.
        Posibles valores: 'error', 'warning', 'debug', 'info'
        Niveles, en orden creciente a su gravedad:
        - debug
        - info
        - warning
        - error
        Si no se especifica level, será por defecto DEBUG
        '''
        if level is None:
            level = 'debug'
        else:
            level = level.lower()
            if not level in ['info', 'debug', 'warning', 'error']:
                raise ValueError('Invalid logging level')

        self.level = level


    def get_level(self):
        '''
        :return: Devuelve el nivel actual de este logger.
        '''
        return self.level