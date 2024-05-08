from pymongo import MongoClient
import json

# Configuración de la conexión a MongoDB
MONGO_HOST = 'mongodb+srv://pp1-rf-user:q0cK1qe153bpS5I0@cluster.0zuctio.mongodb.net'
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT)

# Obtener una referencia a la base de datos
db = client[MONGO_DB]

def searchMdb(label):
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['usuarios']    
    result = []
    filtro = {"label": label}
    documento = collection.find_one(filtro, {"_id": 0,"label":0})
    # Serializar el diccionario como JSON
    json_data = json.dumps(documento)
    result = json.loads(json_data)
    return result
