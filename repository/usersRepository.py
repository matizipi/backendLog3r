import os
from bson import ObjectId
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.connection import db

def get_users_repository():
    collection = db['usuarios']
    usersCursor = collection.find()
    users = list(usersCursor)
    usersCursor.close()

    for user in users:
        user['_id'] = str(user['_id'])
        try:
            for i in range(len(user['horarios'])):
                user['horarios'][i] = str(user['horarios'][i])
        except Exception as e: 
            pass # borrar try-except cuando todos los usuarios de la db tengan el campo "horarios"
    return users

def get_user_repository(user_id, with_horarios=False, with_lugares=False):
    collection = db['usuarios']
    user = None

    if with_horarios or with_lugares:
        pipeline = []
        if with_horarios:
            pipeline = pipeline + [
                {"$unwind": "$horarios" },
                {"$lookup":
                    {
                        "from": "horarios",
                        "localField": "horarios",
                        "foreignField": "_id",
                        "as": "horarios"
                    }
                },
                {"$unwind": "$horarios"},
                {"$group": 
                    {
                        "_id": "$_id",
                        "nombre": {"$first": "$nombre"},
                        "apellido": {"$first": "$apellido"},
                        "dni": {"$first": "$dni"},
                        "rol": {"$first": "$rol"},
                        "email": {"$first": "$email"},
                        "horarios": {"$push": "$horarios"}
                    }
                },
            ]
            
        if with_lugares:
            pipeline = pipeline + [
                {"$lookup":
                    {
                        'from': 'roles',
                        'localField': 'rol',
                        'foreignField': 'nombre',
                        'as': 'lugares'
                    }
                },
                {"$unwind": "$lugares"},
                {"$set":
                    {
                        'lugares': {'$getField':{'field':'lugares','input':'$lugares'}}
                    }
                }
            ]
            
        results = collection.aggregate([{"$match": { "_id": ObjectId(user_id) } }] + pipeline)
        for user in results:
            user['_id'] = str(user['_id'])
            try:
                for horario in user['horarios']:
                    horario['_id'] = str(horario['_id'])
            except Exception as e:
                pass # borrar try-except cuando todos los usuarios de la db tengan el campo "horarios"
    else:
        user = collection.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            try:
                for i in range(len(user['horarios'])):
                    user['horarios'][i] = str(user['horarios'][i])
            except Exception as e:
                pass # borrar try-except cuando todos los usuarios de la db tengan el campo "horarios"
    return user


def get_users_by_role(role_name):
    collection = db['usuarios']
    results = collection.find({ "rol": role_name })
    users = []
    for user in results:
        user['_id'] = str(user['_id'])
        try:
            for i in range(len(user['horarios'])):
                user['horarios'][i]['_id'] = str(user['horarios'][i]['_id'])
        except Exception as e:
            pass # borrar try-except cuando todos los usuarios de la db tengan el campo "horarios"
        users.append(user)

    return users


def create_user_repository(nombre, apellido, dni, rol, horarios, email):
    collection = db['usuarios']
    # Buscar usuario por dni para corroborar si existe
    usuario_existente = collection.find_one({'$or': [{'dni': dni},{'email': email}]},)
    if usuario_existente:
        raise RuntimeError("El usuario ya existe en la base de datos con el id {}".format(usuario_existente['_id']))

    horarios_object = []
    for i in range(len(horarios)):
        horarios_object.append(ObjectId(horarios[i]))

    new_user = {            
        'nombre': nombre,
        'apellido': apellido,
        'dni': int(dni),
        'rol': rol,
        'horarios': horarios_object,
        'email': email
    }
    response = collection.insert_one(new_user)
    new_user['_id'] = str(response.inserted_id)
    new_user['horarios'] = horarios
    guardarHistorialUsuarios(nombre, apellido, dni, rol, horarios_object)
    return new_user


def update_user_repository(user_id, nombre, apellido, dni, rol, horarios, email):
    collection = db['usuarios']
    json_usuario_original = get_user_repository(user_id, with_horarios=True) #obtengo usuario antes de modificarse

    for i in range(len(horarios)):
        horarios[i] = ObjectId(horarios[i])

    result = collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horarios': horarios,
            'email':email
        }}
    )
    if result.modified_count > 0:
        json_usuario_original['horarios'] = [horario['tipo'] + " " + horario['horarioEntrada'] + "-" + horario['horarioSalida'] for horario in json_usuario_original['horarios']]

        json_usuario_modificado = get_user_repository(user_id, with_horarios=True)
        json_usuario_modificado['horarios'] = [horario['tipo'] + " " + horario['horarioEntrada'] + "-" + horario['horarioSalida'] for horario in json_usuario_modificado['horarios']]

        campos_modificados = guardarHistorialUsuariosConCambios(json_usuario_original,json_usuario_modificado)
        normalizarDatosEnLogs(json_usuario_original,campos_modificados)
        notificarCambioDeTitularidad(json_usuario_original,json_usuario_modificado)
    
    return { 'modifiedCount': result.modified_count }

def delete_user_repository(user_id):
    collection = db['usuarios']
    result = collection.delete_one({'_id': ObjectId(user_id)})
    return { 'deletedCount': result.deleted_count }


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
    personal_jerarquico = get_users_by_role("personal jerárquico")
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
    personal_jerarquico = get_users_by_role("personal jerárquico")

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
    
def get_last_estado_by_dni(dni):
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
