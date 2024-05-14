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
    

    
def unionPersonaEspacios(id):
    result = db.usuarios.aggregate([
        {
        '$match': {
            '_id': id  # Filtrar por el ID de la orden deseada
        }
    },
    {
        '$lookup': {
            'from': 'roles',  # Nombre de la colección a unir
            'localField': 'rol',  # Campo de la colección "usuarios" que se relaciona con la otra colección
            'foreignField': 'nombre',  # Campo de la colección "roles" que se relaciona con la otra colección
            'as': 'roles_unidos'  # Nombre del campo donde se almacenarán los documentos de la colección unida
        }
        
    },
    {
        '$project': {
            
            'roles_unidos.lugares': 1,  # Incluir solo el campo lugares de la colección roles
            '_id': 0
            
        }
    }
])
    return result

def registrarLog(mensaje,horario,dni):
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['logs']    
    response = collection.insert_one({
        'horario':horario,
        'mensaje':mensaje,
        'dni':dni
    })
    result = {
        'id': str(response.inserted_id),
        'horario':horario,
        'mensaje':mensaje,
        'dni':dni
    }
    return result   



if __name__== "__main__":
   
    searchMdb()
    