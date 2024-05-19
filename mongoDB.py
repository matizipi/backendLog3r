import os
from pymongo import MongoClient
import certifi
from bson import ObjectId
from bson import json_util
import json

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

def createUser(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image):
    collection = db['usuarios']
    response = collection.insert_one({
        'nombre': nombre,
        'apellido': apellido,
        'dni': int(dni),
        'rol': rol,
        'horariosEntrada': horariosEntrada,
        'horariosSalida': horariosSalida,
        'image': image
    })
    return {
        'id': str(response.inserted_id),
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'rol': rol,
        'horariosEntrada': horariosEntrada,
        'horariosSalida': horariosSalida,
        'image': image
    }

def updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image):
    collection = db['usuarios']
    result = collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'image': image
        }}
    )
    return {'mensaje': 'Usuario actualizado' if result.modified_count > 0 else 'No se realizaron cambios'}

def deleteUser(user_id):
    collection = db['usuarios']
    result = collection.delete_one({'_id': ObjectId(user_id)})
    return {'mensaje': 'Usuario eliminado' if result.deleted_count > 0 else 'Usuario no encontrado'}

def getUsers():
    collection = db['usuarios']
    cursor = collection.find()
    users = list(cursor)
    return json.loads(json_util.dumps(users))


if __name__== "__main__":
   
    searchMdb()
    