from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import numpy as np
from pymongo import MongoClient, ASCENDING
import certifi
from bson.objectid import ObjectId
from bson import ObjectId
from bson import json_util
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import face_recognition
import cv2

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
    
def unionPersonaEspacios(user):
    rolesCursor = db["roles"].find({"nombre":user["rol"]})
    lugares_set = set()
    for doc in rolesCursor:
        lugares_set.update(doc["lugares"])
    lugares = list(lugares_set)

    rolesCursor.close()

    user["lugares"] = lugares

    return user


def createUser(nombre, apellido, dni, rol, horariosEntrada, horariosSalida,email):
    collection = db['usuarios']
    # Buscar usuario por dni para corroborar si existe
    usuario_existente = collection.find_one({'$or': [{'dni': dni},{'email': email}]})

    if usuario_existente ==None:

        response = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'email':email
        })       
        guardarHistorialUsuarios(nombre, apellido, dni, rol, horariosEntrada, horariosSalida)
    object_id = usuario_existente['_id'] if usuario_existente else None
    return {'mensaje': 'Usuario creado' if usuario_existente==None else "El usuario ya existe en la base de datos con el id {}".format(object_id),}
 

def updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida,email):
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
            'email':email
        }}
    )
    if result.modified_count > 0:
        json_usuario_modificado = getUser(user_id) #obtengo usuario modificado       
        campos_modificados = guardarHistorialUsuariosConCambios(json_usuario_original,json_usuario_modificado)
        normalizarDatosEnLogs(json_usuario_original,campos_modificados)
        notificarCambioDeTitularidad(json_usuario_original,json_usuario_modificado)
    return {'mensaje': 'Usuario actualizado' if result.modified_count > 0 else 'No se realizaron cambios'}

def deleteUser(user_id):
    collection = db['usuarios']
    result = collection.delete_one({'_id': ObjectId(user_id)})
    return {'mensaje': 'Usuario eliminado' if result.deleted_count > 0 else 'Usuario no encontrado'}

def getUser(user_id):
    collection = db['usuarios']
    user = collection.find_one({'_id': ObjectId(user_id)})
    return json.loads(json_util.dumps(user))


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
    
    dni = campos_modificados.get('dni') if campos_modificados.get('dni') else None
    collection = db['historial_usuarios']
    response = collection.insert_one({
        'nombre': campos_modificados.get('nombre'),
        'apellido': campos_modificados.get('apellido'),
        'dni': dni,
        'rol': campos_modificados.get('rol'),
        'horariosEntrada': campos_modificados.get('horariosEntrada'),
        'horariosSalida': campos_modificados.get('horariosSalida'),
        'image': campos_modificados.get('image'),
        'email': campos_modificados.get('email'),
        'fechaDeCambio': datetime.now(),
        'usuarioResponsable': ''
    })
    return campos_modificados

def guardarHistorialUsuarios(nombre, apellido, dni, rol, horariosEntrada, horariosSalida):
    collection = db['historial_usuarios']
    result = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horariosEntrada': horariosEntrada,
            'horariosSalida': horariosSalida,
            'fechaDeCambio':datetime.now(),
            'usuarioResponsable':'RRHH'
        })
def normalizarDatosEnLogs(json_usuario_original,cambios): 
    dni = json_usuario_original.get('dni')
    logs = db['logs']   
    filtro = {'dni': dni}           
    actualizacion = {'$set': cambios}

    # Ejecutar la actualización
    logs.update_many(filtro, actualizacion)  

def notificarCambioDeTitularidad(json_usuario_original,json_usuario_modificado):
    asunto="Notificación sobre cambio de titularidad"
    collection = db['usuarios']
    personal_jerarquico = collection.find({"rol": "personal jerárquico"})
    emails = [user['email'] for user in personal_jerarquico]

    mensaje=generar_cuerpo_cambio_titularidad(json_usuario_original,json_usuario_modificado)

    for email in emails:
        send_email(email, asunto, mensaje)


def generar_cuerpo_cambio_titularidad(original, modificado):
    cambios = []
    for key in original:
        if key in modificado and original[key] != modificado[key]:
            cambios.append(f"{key}: {original[key]} -> {modificado[key]}")
    
    if not cambios:
        return "No se han realizado modificaciones."
    
    cuerpo = "Se han realizado los siguientes cambios en la información del usuario:\n\n"
    cuerpo += "\n".join(cambios)
    return cuerpo

def notificarCorte(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte):
    asunto="Notificación sobre corte de Internet (Log3rApp)"
    collection = db['usuarios']
    personal_jerarquico = collection.find({"rol": "personal jerárquico"})
    emails = [user['email'] for user in personal_jerarquico]

    mensaje=generar_cuerpo_notificacion_corte(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte)

    for email in emails:
        send_email(email, asunto, mensaje)

def generar_cuerpo_notificacion_corte(horarioDesconexion, horarioReconexion, cantRegSincronizados,periodoDeCorte):       
    cuerpo = (
        f"Se ha detectado un corte de Internet en la aplicación:\n\n"
        f"Horario de Desconexión: {horarioDesconexion}\n"
        f"Horario de Reconexión: {horarioReconexion}\n"
        f"Cantidad de Registros Sincronizados: {cantRegSincronizados}\n\n"
        f"Tiempo total sin conexión de internet: {periodoDeCorte} (horas\minutos\segundos) \n\n"
        f"Log3rApp by AlphaTeam"
    )
    return cuerpo


def send_email(to_email, subject, message):

    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    smtp_user = os.getenv('OUTLOOK_USER') 
    smtp_password = os.getenv('OUTLOOK_PASSWORD') 
    
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
        # Convertir la imagen a RGB si no lo está
        if len(imagen.shape) == 2:  # Escala de grises
            imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        elif imagen.shape[2] == 4:  # RGBA a RGB
            imagen = cv2.cvtColor(imagen, cv2.COLOR_RGBA2RGB)
        elif imagen.shape[2] == 3:  # Ya está en RGB
            pass
        else:
            raise ValueError("Tipo de imagen no soportado")

        # Encontrar la ubicación del rostro en la imagen
        posrostro_entrada = face_recognition.face_locations(imagen)
        if not posrostro_entrada:
            # No se encontró ningún rostro en la imagen
            return None
        
        # Obtener los embeddings del primer rostro encontrado
        vector_rostro_entrada = face_recognition.face_encodings(imagen, known_face_locations=[posrostro_entrada[0]])
        if vector_rostro_entrada:
            return vector_rostro_entrada
        else:
            return None
    except Exception as e:
        print(f"Error procesando la imagen: {e}")
        return None
    
def getLastEstadoByDni(dni):
    logs = db['logs']
    try:
        dni = int(dni)
        
        result = logs.find({'dni': dni}).sort('horario', -1).limit(1)
        last_log = list(result)

        if last_log:
            last_log[0]['_id'] = str(last_log[0]['_id'])
            return last_log[0], 200
        else:
            return {}, 404
    except ValueError:
        return {'error': 'El parámetro dni debe ser un número entero'}, 400
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return {'error': mensaje_error}, 500