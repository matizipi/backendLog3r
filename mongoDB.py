from datetime import datetime, time, timedelta
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from bson import ObjectId
from bson import json_util
import json
import face_recognition

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
    # Cargar las variables del archivo .env
    load_dotenv()
    # Configuración de la conexión a MongoDB
    MONGO_URI = os.getenv('MONGO_URI')  
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database()  # Obtener la base de datos desde la URI
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
        'dni':int(dni),
        'estado':estado,
        'tipo':tipo
    }
    return result   

def createUser(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image,email):
    collection = db['usuarios']
    # Buscar usuario por dni para corroborar si existe
    usuario_existente = collection.find_one({'$or': [{'dni': dni},{'email': email}]
    })

    if usuario_existente==None:
        '''try:
            imagen = getEmbeddigs(image)
        except Exception as e:
            print(f"Error al abrir la imagen: {e}")'''
       
        response = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'image': None,
            'email': email
        })       
        guardarHistorialUsuarios(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image)
    return {'mensaje': 'Usuario creado' if usuario_existente==None else 'El usuario ya existe en la base de datos con el id ${response.inserted_id}',}
 

def updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image, email):
    collection = db['usuarios']
    json_usuario_original = getUser(user_id) #obtengo usuario antes de modificarse
    result = collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'image': image,
            'email': email
        }}
    )
    if result.modified_count > 0:
        json_usuario_modificado = getUser(user_id) #obtengo usuario modificado       
        campos_modificados = guardarHistorialUsuariosConCambios(json_usuario_original,json_usuario_modificado)
        normalizarDatosEnLogs(json_usuario_original,campos_modificados)
    return {'mensaje': 'Usuario actualizado' if result.modified_count > 0 else 'No se realizaron cambios'}

def deleteUser(user_id):
    collection = db['usuarios']
    result = collection.delete_one({'_id': ObjectId(user_id)})
    return {'mensaje': 'Usuario eliminado' if result.deleted_count > 0 else 'Usuario no encontrado'}

def getUser(user_id):
    collection = db['usuarios']
    user = collection.find_one({'_id': ObjectId(user_id)})
    return json.loads(json_util.dumps(user))

def obtener_logs_dia_especifico(fecha):
    load_dotenv()
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database()
    collection = db['logs']

    # Convertir la fecha en un rango de inicio y fin del día
    fecha_inicio = datetime.combine(fecha, datetime.min.time()) #la hora mínima (00:00:00).
    fecha_fin = fecha_inicio + timedelta(days=1)

    # Pipeline de agregación
    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': fecha_inicio,
                    '$lt': fecha_fin
                }
            }
        }
    ]

    # Ejecutar el pipeline
    resultados = list(collection.aggregate(pipeline))

    # Convertir los resultados a JSON
    resultados_json = json.dumps(resultados, default=str)

    return resultados_json

def getUsers():
    collection = db['usuarios']
    cursor = collection.find()
    users = list(cursor)
    return json.loads(json_util.dumps(users))

def guardarHistorialUsuariosConCambios(json_usuario_original,json_usuario_modificado):
     # Lista para almacenar los campos modificados
    campos_modificados = {}

    # Compara los valores de cada campo
    for campo, valor_actual in json_usuario_modificado.items():
        if campo in json_usuario_original and json_usuario_original[campo] != valor_actual:
            campos_modificados[campo] = valor_actual
    
    collection = db['historial_usuarios']
    response = collection.insert_one({            
            'nombre': campos_modificados.get('nombre') if 'nombre' in  campos_modificados.keys else '',
            'apellido': campos_modificados.get('apellido') if 'apellido' in  campos_modificados.keys else '',
            'dni': int(campos_modificados.get('dni')) if 'dni' in  campos_modificados.keys else '',
            'rol': campos_modificados.get('rol') if 'rol' in  campos_modificados.keys else '',
            'horariosEntrada': campos_modificados.get('horariosEntrada') if 'horariosEntrada' in  campos_modificados.keys else '',
            'horariosSalida': campos_modificados.get('horariosSalida') if 'horariosSalida' in  campos_modificados.keys else '',
            'image': campos_modificados.get('image') if 'image' in  campos_modificados.keys else '',
            'fechaDeCambio':datetime.now(),
            'usuarioResponsable':''
        })
    return campos_modificados

def guardarHistorialUsuarios(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image):
    collection = db['historial_usuarios']
    result = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'image': image,
            'fechaDeCambio':datetime.now(),
            'usuarioResponsable':''
        })
def normalizarDatosEnLogs(json_usuario_original,cambios): 
    dni = json_usuario_original.get('dni')
    logs = db['logs']   
    filtro = {'dni': dni}           
    actualizacion = {'$set': cambios}

    # Ejecutar la actualización
    logs.update_many(filtro, actualizacion)  
        
def getEmbeddigs(imagen):    
    posrostro_entrada=face_recognition.face_locations(imagen)[0]
    if not posrostro_entrada:
            # No se encontraron rostros en la imagen
            raise ValueError("No se encontraron rostros en la imagen proporcionada")    
    vector_rostro_entrada=face_recognition.face_encodings(imagen,known_face_locations=[posrostro_entrada]) 
    
    return vector_rostro_entrada



if __name__== "__main__":
   
    searchMdb()
    
