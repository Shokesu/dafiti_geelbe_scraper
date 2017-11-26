
from copy import deepcopy
from os.path import dirname, join, normpath, basename, isfile
import importlib.util
from re import match
import inspect, sys

class Config:
    '''
    Esta clase representa una configuración para el dafiti_geelbe_scraper.
    '''
    def __init__(self, vars = {}):
        '''
        Inicializa la instancia.
        :param vars: Es un diccionario donde los claves son los nombres de las variables,
        y los valores, los valores de cada una de ellas.
        :param root_path: Es un parámetro opcional que indica ruta raíz para procesar las
        rutas relativas especificadas en las variables de configuración. Por defecto es
        el directorio padre de este script
        '''
        self.vars = deepcopy(vars)

        config = self
        class PathProxy:
            def __getattr__(self, item):
                return config.get_path(var = item, default = None)
        self.path = PathProxy()

    def copy(self):
        return Config(self.vars)

    def get_value(self, var, default = None):
        '''
        Devuelve el valor de la variable cuyo nombre se indica como parámetro.
        :param default: Es el valor por defecto que se devolverá como salida si la variable no
        se ha establecido en la configuración, por defecto None
        '''
        return self.vars[var] if var in self.vars else default


    def has_value(self, var, value):
        '''
        Comprueba si una variable de configuración tiene el valor indicado como parámetro.
        has_value('var', None) devuelve True si la variable 'var' es None o bien no se ha
        establecido.

        :param var:
        :param value:
        :return:
        '''
        return self.get_value(var) == value


    def is_set(self, var):
        '''
        Comprueba si una variable configuración se ha establecido.
        :param var:
        :return:
        '''
        return var in self.vars


    def set_value(self, var, value = None):
        '''
        Establece el valor de una variable de configuración.
        :param var: Es el nobmre de la variable.
        :param value: Es el nuevo valor de la variable. (Por defecto es None)
        '''
        self.vars[var] = value

    def is_true(self, var):
        '''
        Es igual que has_value(var, True)
        :param var:
        :return:
        '''
        return self.has_value(var, True)


    def get_path(self, var, default = None):
        '''
        Devuelve la variable indicada como parámetro (ruta a un fichero) normalizada (se procesan
        rutas relativas) Si la ruta no es válida devuelve None
        :param var:
        :param default:
        :return:
        '''
        value = self.get_value(var)
        if value is None or not isinstance(value, (str, Path)):
            return default
        if isinstance(value, str):
            value = Path(value)
        return str(value)


    def __getattr__(self, item):
        return self.get_value(var = item, default = None)


    @staticmethod
    def load_from_file(file):
        '''
        Carga la configuración desde un fichero.
        Solo se cargarán variables cuyos valores son datos básicos: Booleanos, números, strings e instancias
        de la clase Path
        :param file: Es la ruta del fichero de configuración absoluta o relativa al directorio
        padre de este script.
        :return: Devuelve una instancia de la clase Config.
        '''
        try:
            location = file
            config_module_name = match('^([^\.]+)(\..*)?$', basename(location)).group(1)

            spec = importlib.util.spec_from_file_location('config.{}'.format(config_module_name), location)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)

            config_vars = [(key, value) for key, value in config_module.__dict__.items() if not match('^__.*__$', key)]
            config_vars = [(key, value) for key, value in config_vars if isinstance(value, (int, float, str, bool, Path))]
            return Config(dict(config_vars))
        except Exception as e:
            raise Exception('Failed to load configuration from configuration file: {}'.format(e))



    def override(self, other):
        '''
        Sobrecarga otra configuración con esta. Los valores de las variables en la nueva configuración,
        sustituyen a los valores de esta configuración.
        :param other: Otra configuración (Instancia de la clase Config)
        :return:
        '''
        self.vars.update(other.vars)


    def check(self):
        '''
        Valida la configuración actual. Si la configuración actual no es válida, genera una
        excepción
        :return:
        '''
        try:
            # TODO
            pass
        except Exception as e:
            raise ValueError('Configuration is not valid: {}'.format(str(e)))

    def __str__(self):
        return str(self.vars)




class DefaultConfig:
    '''
    Es la configuración por defecto del dafiti_geelbe_scraper. Usa el patrón singleton.
    La configuración por defecto esta en el fichero "default.conf.py" en este mismo directorio.
    '''

    class __Singleton(Config):
        def __init__(self):
            super().__init__()
            self.override(Config.load_from_file(join(dirname(__file__), 'configs', 'default.conf.py')))

    singleton = None
    def __init__(self):
        if DefaultConfig.singleton is None:
            DefaultConfig.singleton = DefaultConfig.__Singleton()

    def __getattr__(self, item):
        return getattr(DefaultConfig.singleton, item)

    def __str__(self):
        return str(DefaultConfig.singleton)


class GlobalConfig:
    '''
    Esta clase representa la configuración global del dafiti_geelbe_scraper.
    Usa el patrón singleton.
    '''

    class __Singleton(Config):
        def __init__(self):
            super().__init__()
            self.override(default_config)


    singleton = None
    def __init__(self):
        if GlobalConfig.singleton is None:
            GlobalConfig.singleton = GlobalConfig.__Singleton()

    def __getattr__(self, item):
        return getattr(GlobalConfig.singleton, item)

    def __str__(self):
        return str(GlobalConfig.singleton)


class Path:
    '''
    Esta clase se usa para configurar rutas a ficheros en las variables de configuración.
    '''
    def __init__(self, file):
        root_path = dirname(inspect.getfile(sys._getframe(1)))
        self.path = normpath(join(root_path, file))
        #if not isfile(self.path):
        #    raise ValueError('File "{}" doesnt exist'.format(self.path))

    def __str__(self):
        return self.path

    def __repr__(self):
        return repr(self.path)


def path(*args, **kwargs):
    '''
    Es un shortcut del constructor de clase Path.
    '''
    return Path(*args, **kwargs)



default_config = DefaultConfig()
global_config = GlobalConfig()
