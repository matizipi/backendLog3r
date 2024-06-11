import os
import certifi
from pymongo import MongoClient

# Configuración de la conexión a MongoDB
MONGO_HOST = os.getenv('MONGO_URI') # por seguridad no subir url al repo, crear archivo .env local
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())

# Obtener una referencia a la base de datos
db = client[MONGO_DB]