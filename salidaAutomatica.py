from pymongo import MongoClient, errors
from datetime import datetime, timedelta, timezone
import schedule
import certifi
import os
from dotenv import load_dotenv
import time
from mongoDB import registrarLog

print("Inicio de salidaAutomatica.py", flush=True)  # Asegura que el mensaje se imprima) 

# Cargar las variables del archivo .env
load_dotenv()

# Configuración de la conexión a MongoDB
MONGO_URI = os.getenv('MONGO_URI')  # por seguridad no subir URL al repo, crear archivo .env local

# Intentar conectar a MongoDB con manejo de errores
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database()  # Obtener la base de datos desde la URI
    logs_collection = db['logs']
    print("Conexión a MongoDB establecida correctamente.",flush=True)
except errors.ServerSelectionTimeoutError as err:
    print(f"Error al conectar a MongoDB: {err}")
    exit(1)
except errors.ConfigurationError as err:
    print(f"Configuración de MongoDB incorrecta: {err}",flush=True)
    exit(1)
except Exception as err:
    print(f"Error inesperado al conectar a MongoDB: {err}",flush=True)
    exit(1)

def automatic_log_out():
    start = time.time()
    utc_minus_3 = timezone(timedelta(hours=0)) #!pasar las hores -3 si que quiere horario para argentina
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
        print(logs,flush=True)
    except errors.PyMongoError as err:
        print(f"Error al ejecutar el pipeline de agregación: {err}")
        return
 # Procesar los logs y actualizar el estado si es necesario
    for log in logs:
        if log.get('estado') == 'ingresando':  # log.get evitará que se lance un error KeyError si la clave 'estado' no está presente en un documento específico.            
            try:
                registrarLog(now, log.get('nombre'), log.get('apellido'), log.get('dni'), 'saliendo', 'automatico')
            except errors.PyMongoError as err:
                print(f"Error al registrar el log: {err}",flush=True)
   
    finish = time.time()
    timeDuration = finish - start
    print("Proceso de logout automático completado en : ",timeDuration,flush=True)

# Programar la tarea diaria a las 23:59
schedule.every().day.at("16:13").do(automatic_log_out)

print("Iniciando bucle de ejecución",flush=True)
# Mantener el script en ejecución para que se ejecute la tarea programada
while True:
    schedule.run_pending()
    time.sleep(60) 


