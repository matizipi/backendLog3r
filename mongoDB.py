import os
from pymongo import MongoClient
import certifi
from bson.objectid import ObjectId


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

def getImageEmbeddings():
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['imagenes']
    filtro = {}
    cursor = collection.find(filtro)
    return cursor


# Function to get user by ObjectId
def getUserByObjectid(object_id):
    try:
        # Access the collection
        collection = db['usuarios']

        # Find the user
        user = collection.find_one({"_id": object_id})
        return user
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def unionPersonaEspacios(id):
    result = db.usuarios.aggregate([
        {
        '$match': {
            '_id': id  # Filtrar por el ID de la orden deseada
        }
    },
    {
        '$lookup': {
            "from": "roles",
            "localField": "rol",
            "foreignField": "nombre",
            "as": "rol_info"
        }
        
    },{
        '$project': {
            
            "_id": 1,
            "label": 1,
            "nombre": 1,
            "apellido": 1,
            "dni": 1,
            "rol": 1,
            "horariosEntrada": 1,
            "horariosSalida": 1,
            "image": 1,
            "lugares": {"$first":"$rol_info.lugares"}
        }
    }
])
    return result

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
    