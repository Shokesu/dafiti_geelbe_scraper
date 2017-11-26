

'''
Esta es la configuración por defecto del dafiti_geelbe_scraper de TripAdvisor
'''
from config import path

# -----------------------------------------------
# CONFIGURACIÓN DE ESCRAPEO
# TODO
# -----------------------------------------------

# -----------------------------------------------
# CONFIGURACIÓN DE SALIDA DE DATOS

# Fichero de base de datos sqlite de salida de los datos escrapeados.
OUTPUT_DATA_TO_SQLITE = path('data/articles.db')

# -----------------------------------------------


# -----------------------------------------------
# CONFIGURACIÓN DE LOGS Y DEPURACIÓN DEL SCRAPER

# Establece el nivel de logging. Posibles valores: 'INFO', 'WARNING', 'ERROR', 'DEBUG'
LOG_LEVEL = 'WARNING'

# Muestra todos los mensajes de logging generados por la salida estándard.
OUTPUT_LOGS_TO_STDOUT = False

# Muestra mensajes de logging por la salida estandard generados por la librería pony orm.
# No tiene efecto si LOG_LEVEL ES 'INFO' o si la variable OUTPUT_LOGS_TO_STDOUT es False
OUTPUT_PONY_LOGS_TO_STDOUT = False


# -----------------------------------------------

# -----------------------------------------------
# CONFIGURACIÓN DE EJECUCIÓN DEL SCRAPER
# -----------------------------------------------

# Establece la url del proxy usado para prcoesar el código javascript de las páginas.
SPLASH_PROXY_URL = 'http://localhost:8050'