
import pony
from pony.orm import Database as PonyDatabase, set_sql_debug
from config import global_config

class Database:
    '''
    Representa una base de datos.
    Antes de interactuar con el esquema, debe invocarse el método generate_mapping
    para generar el mapeado orm a la base de datos sqlite.
    '''
    class __Singleton(PonyDatabase):
        def __init__(self):
            db_path = global_config.path.OUTPUT_DATA_TO_SQLITE

            logs_enabled = all([
                global_config.path.OUTPUT_DATA_TO_SQLITE,
                global_config.OUTPUT_PONY_LOGS_TO_STDOUT,
                global_config.LOG_LEVEL.lower() in ['debug', 'warning', 'error']
            ])

            super().__init__()
            super().bind(provider='sqlite', filename=db_path, create_db=True)

            set_sql_debug(logs_enabled)

            self.mapping_generated = False

        def generate_mapping(self, create_tables = True, **kwargs):
            # Antes de generar el mapeado, importamos las entidades del modelo.
            from entities.article import Article
            super().generate_mapping(create_tables = create_tables, **kwargs)

    singleton = None
    def __init__(self):
        if self.singleton is None:
            self.singleton = self.__Singleton()

    def __getattr__(self, item):
        return getattr(self.singleton, item)


# Creamos una base de datos para artículos.
db = Database()


# Decorador de sesión de base de datos
db_session = pony.orm.db_session



