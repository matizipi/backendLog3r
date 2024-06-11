import signal
import sys
import logging
from pymongo import MongoClient, errors
from datetime import datetime, timedelta, timezone
import schedule
import certifi
import os
from dotenv import load_dotenv
import time
from repository.logsRepository import registrarLog

load_dotenv()

# Configurar logging a la consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)

logging.info("Inicio de salidaAutomatica.py")  # Asegura que el mensaje se registre

# Configuración de la conexión a MongoDB
MONGO_HOST = os.getenv('MONGO_URI') # por seguridad no subir url al repo, crear archivo .env local
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Intentar conectar a MongoDB con manejo de errores
try:
    client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())
    # Obtener una referencia a la base de datos
    db = client[MONGO_DB]    
    logs_collection = db['logs']
    logging.info("Conexión a MongoDB establecida correctamente.")
except errors.ServerSelectionTimeoutError as err:
    logging.error(f"Error al conectar a MongoDB: {err}")
    exit(1)
except errors.ConfigurationError as err:
    logging.error(f"Configuración de MongoDB incorrecta: {err}")
    exit(1)
except Exception as err:
    logging.error(f"Error inesperado al conectar a MongoDB: {err}")
    exit(1)

def signal_handler(sig, frame):
    print(sig)
    client.close()
    print('finish salidaAutomatica.py!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def automatic_log_out():
    start = time.time()
    utc_minus_3 = timezone(timedelta(hours=0)) # Ajustar a -3 si se quiere el horario de Argentina
    # Obtener la fecha actual en UTC-03:00 y la fecha de ayer en UTC-03:00
    now = datetime.now(utc_minus_3)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    # Pipeline de agregación para obtener el último log de cada usuario por 'dni'
    pipeline = [
        {
            '$match': {
                'horario': {'$gte': yesterday, '$lt': today}
            }
        },
        {
            '$sort': {'horario': 1}
        },
        {
            '$group': { 
                '_id': '$dni',
                'last_log': {'$last': '$$ROOT'}
            }
        },
        {
            '$replaceRoot': {'newRoot': '$last_log'}
        }
    ]

    # Ejecutar el pipeline de agregación
    try:
        logs = list(logs_collection.aggregate(pipeline))
        logging.info(f"Logs obtenidos: {logs}")
    except errors.PyMongoError as err:
        logging.error(f"Error al ejecutar el pipeline de agregación: {err}")
        return

    # Procesar los logs y actualizar el estado si es necesario
    for log in logs:
        if log.get('estado') == 'Ingresando' or 'ingresando' :  # log.get evitará que se lance un error KeyError si la clave 'estado' no está presente en un documento específico.            
            try:
                registrarLog(now, log.get('nombre'), log.get('apellido'), log.get('dni'), 'Saliendo', 'Automatico')
                logging.info(f"Registrado log automático para {log.get('dni')}")
            except errors.PyMongoError as err:
                logging.error(f"Error al registrar el log: {err}")
   
    finish = time.time()
    timeDuration = finish - start
    logging.info(f"Proceso de logout automático completado en: {timeDuration}")

# Programar la tarea diaria a las 23:59
schedule.every().day.at("23:59","America/Argentina/Buenos_Aires").do(automatic_log_out)

logging.info("Iniciando bucle de ejecución")
# Mantener el script en ejecución para que se ejecute la tarea programada
while True:
    schedule.run_pending()
    time.sleep(60)