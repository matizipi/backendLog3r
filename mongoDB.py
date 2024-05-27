from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import numpy as np
from pymongo import MongoClient, ASCENDING
import certifi
from bson import ObjectId
from bson import json_util
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        image_list = vectorizarImagen(image)[0].tolist()
             
        response = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'image': image_list,
            'email':email
        })       
        guardarHistorialUsuarios(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image_list)
    return {'mensaje': 'Usuario creado' if usuario_existente==None else 'El usuario ya existe en la base de datos con el id ${response.inserted_id}',}
 

def updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image,email):
    collection = db['usuarios']
    json_usuario_original = getUser(user_id) #obtengo usuario antes de modificarse
    if isinstance(image, list)==False:
        image = vectorizarImagen(image)[0].tolist()    
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
            'email':email
        }}
    )
    if result.modified_count > 0:

        json_usuario_modificado = getUser(user_id) #obtengo usuario modificado        
        label = collection.find_one({ '_id': ObjectId(user_id)}, { 'label': 1, '_id': 0 })
        campos_modificados = guardarHistorialUsuariosConCambios(json_usuario_original,label,json_usuario_modificado)
        normalizarDatosEnLogs(campos_modificados,label)
        notificarAlPersonalJerarquico(json_usuario_original,json_usuario_modificado)

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
    collection = db['logs']
    
    # Convertir la fecha en un rango de inicio y fin del día
    fecha_inicio = datetime.combine(fecha, datetime.min.time())
    fecha_fin = fecha_inicio + timedelta(days=1)
    #print(f"Rango de fecha: {fecha_inicio} - {fecha_fin}")  # Depuración

    # Pipeline de agregación
    pipeline = [
        {
            '$match': {
                'horario': {
                    '$gte': fecha_inicio,
                    '$lt': fecha_fin
                }
            }
        }
    ]

    # Ejecutar el pipeline
    resultados = list(collection.aggregate(pipeline))
    print(f"Resultados encontrados: {resultados}")  # Depuración

    # Convertir los resultados a un formato adecuado para JSON
    resultados_json = []
    for resultado in resultados:
        resultado['_id'] = str(resultado['_id'])  # Convertir ObjectId a string
        resultados_json.append(resultado)

    return resultados_json  # Devolver como una lista de diccionarios

def getUsers():
    collection = db['usuarios']
    cursor = collection.find()
    users = list(cursor)
    return json.loads(json_util.dumps(users))

def guardarHistorialUsuariosConCambios(json_usuario_original,label,json_usuario_modificado):
     # Lista para almacenar los campos modificados
    campos_modificados = {}

    # Compara los valores de cada campo
    for campo, valor_actual in json_usuario_modificado.items():
        if campo in json_usuario_original and json_usuario_original[campo] != valor_actual:
            campos_modificados[campo] = valor_actual
    
    collection = db['historial_usuarios']
    response = collection.insert_one({
        'nombre': campos_modificados.get('nombre'),
        'apellido': campos_modificados.get('apellido'),
        'dni': int(campos_modificados.get('dni')),
        'rol': campos_modificados.get('rol'),
        'horariosEntrada': campos_modificados.get('horariosEntrada'),
        'horariosSalida': campos_modificados.get('horariosSalida'),
        'image': campos_modificados.get('image'),
        'email': campos_modificados.get('email'),
        'fechaDeCambio': datetime.now(),
        'usuarioResponsable': ''
    })
    return campos_modificados

def guardarHistorialUsuarios(label,nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image):
    collection = db['historial_usuarios']
    result = collection.insert_one({
            'label':label,
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
def normalizarDatosEnLogs(cambios,label): 
    logs = db['logs']   
    filtro = {'label': label}           
    actualizacion = {'$set': cambios}

    # Ejecutar la actualización
    logs.update_many(filtro, actualizacion)  

def notificarAlPersonalJerarquico(json_usuario_original,json_usuario_modificado):
    asunto="Notificación sobre cambio de titularidad"
    collection = db['usuarios']
    personal_jerarquico = collection.find({"rol": "personal jerárquico"})
    emails = [user['email'] for user in personal_jerarquico]

    mensaje=generar_cuerpo_del_correo(json_usuario_original,json_usuario_modificado)

    for email in emails:
        send_email(email, asunto, mensaje)


def generar_cuerpo_del_correo(original, modificado):
    cambios = []
    for key in original:
        if key in modificado and original[key] != modificado[key]:
            cambios.append(f"{key}: {original[key]} -> {modificado[key]}")
    
    if not cambios:
        return "No se han realizado modificaciones."
    
    cuerpo = "Se han realizado los siguientes cambios en la información del usuario:\n\n"
    cuerpo += "\n".join(cambios)
    return cuerpo

def send_email(to_email, subject, message):

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'log3rapp@gmail.com'
    smtp_password = 'log3rAlpha'

    # Configuración del mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(message, 'plain'))

    # Conectar al servidor SMTP y enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f'Correo enviado a {to_email}')
    except Exception as e:
        print(f'Error al enviar el correo a {to_email}: {e}')

        
def vectorizarImagen(imagen):
    try:
        # Encontrar la ubicación del rostro en la imagen
        posrostro_entrada = face_recognition.face_locations(imagen)[0]
        if not posrostro_entrada:
            # No se encontró ningún rostro en la imagen
            return None
        
        # Obtener los embeddings del primer rostro encontrado        
        vector_rostro_entrada = face_recognition.face_encodings(imagen, known_face_locations=[posrostro_entrada])        
        if vector_rostro_entrada:
            return vector_rostro_entrada
        else:
            return None
    except Exception as e:
         print(f"Error procesando la imagen: {e}")
def leerTHRESHOLD():
    collection = db['configuraciones']
    
    cursor = collection.find().sort({"fechaDeCambio":-1}).limit(1)
    THRESHOLDD_document=cursor.next()
    cursor.close()
    return THRESHOLDD_document["valor"]

def insertarTHRESHOLD(THRESHOLD):
    collection = db['configuraciones']
    collection.insert_one({
        
        'nombre':"certeza",
        'valor':THRESHOLD,
        'usuarioDeCambio':"inicial",
        'fechaDeCambio':datetime.now()})


if __name__== "__main__":
   
    searchMdb()
    