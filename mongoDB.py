import os
from datetime import datetime
from pymongo import MongoClient
import certifi
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de la conexión a MongoDB
MONGO_HOST = os.getenv('MONGO_URI') # por seguridad no subir url al repo, crear archivo .env local
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())

# Obtener una referencia a la base de datos
db = client[MONGO_DB]

def getImageEmbeddings():
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['imagenes']
    filtro = {}
    cursor = collection.find(filtro)
    return cursor
    
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
        'horarios': campos_modificados.get('horarios'),
        'email': campos_modificados.get('email'),
        'fechaDeCambio': datetime.now(),
        'usuarioResponsable': ''
    })
    return campos_modificados

def guardarHistorialUsuarios(nombre, apellido, dni, rol, horarios):
    collection = db['historial_usuarios']
    result = collection.insert_one({            
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horarios': horarios,
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
        f"Tiempo total sin conexión de internet: {periodoDeCorte} (horas\\minutos\\segundos) \n\n"
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
