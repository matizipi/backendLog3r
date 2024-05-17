from pymongo import MongoClient
from datetime import datetime,timedelta
import schedule
import certifi
import os
from dotenv import load_dotenv
import time

# Cargar las variables del archivo .env
load_dotenv()

# Configuración de la conexión a MongoDB
MONGO_HOST = os.getenv('MONGO_URI') # por seguridad no subir url al repo, crear archivo .env local
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())

# Obtener una referencia a la base de datos
db = client[MONGO_DB]

logs_collection = db['logs']

def automatic_log_out():
    # Obtener la fecha de hoy y ayer para el filtro de logs
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
    logs = list(logs_collection.aggregate(pipeline))
    print(logs)
    # Procesar los logs y actualizar el estado si es necesario
    '''for log in logs:
        if log.get('estado') == 'ingresando':  ##log.get evitará que se lance un error KeyError si la clave 'estado' no está presente en un documento específico.          
            logs_collection.update_one(
                {'_id': log['_id']},
                {'$set': {'estado': 'saliendo', 'tipo': 'automatico'}}
            )'''
    for log in logs:
     if log.get('mensaje'):  #log.get evitará que se lance un error KeyError si la clave 'estado' no está presente en un documento específico.          
        logs_collection.update_one(
            {'_id': log['_id']},
            {'$set': {'mensaje': 'prueba de automatico'}}
        )

    print("Proceso de logout automático completado.")

# Programar la tarea diaria a las 23:59
schedule.every().day.at("17:35").do(automatic_log_out)

# Mantener el script en ejecución para que se ejecute la tarea programada
while True:
    schedule.run_pending()
    time.sleep(86400)# cantidad de segundos para que se ejecute una vez al dia


    
    