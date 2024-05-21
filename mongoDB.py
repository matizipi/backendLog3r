import os
from pymongo import MongoClient
import certifi

# Configuración de la conexión a MongoDB
MONGO_HOST = os.getenv('MONGO_URI') # por seguridad no subir url al repo, crear archivo .env local
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())

# Obtener una referencia a la base de datos
db = client[MONGO_DB]

def searchMdb():
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['usuarios']    
    filtro = {}
    cursor = collection.find(filtro)
    return cursor
    

    
def unionPersonaEspacios(user):
    rolesCursor = db.roles.find({"nombre":{"$in":user["rol"]}})
    lugares_set = set()
    for doc in rolesCursor:
        lugares_set.update(doc["lugares"])
    lugares = list(lugares_set)

    rolesCursor.close()

    user["lugares"] = lugares

    return user

def registrarLog(horario,nombre,apellido,dni,estado,tipo):
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['logs']    
    response = collection.insert_one({
        'horario':horario,
        'nombre':nombre,
        'apellido':apellido,
        'dni':int(dni),
        'estado':estado,
        'tipo':tipo})
    
    result = {
        'id': response.inserted_id,
        'horario':horario,
        'nombre':nombre,
        'apellido':apellido,
        'dni':dni,
        'estado':estado,
        'tipo':tipo
    }
    return result   


if __name__== "__main__":
   
    searchMdb()
    