import time
from bson import ObjectId
from datetime import datetime
from database.connection import db
from repository.reportesRepository import notificarCambioDeTitularidad

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
        notificarCambioDeTitularidad(nombre,apellido,json_usuario_original,json_usuario_modificado)
    
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

def chequearExistenciaDeUsuarios(registros):
    listaIncompatibles = []
    collection = db['usuarios']

    for registro in registros:
        try:
            # Acceder a los valores del diccionario
            dni = registro.get('dni')
            nombre = registro.get('nombre')
            apellido = registro.get('apellido')
            
            usuario = collection.find_one({
                'dni': dni,
                'nombre': nombre,
                'apellido': apellido
            })
            
            if usuario is None:
                listaIncompatibles.append(registro)
        except Exception as e:
            print(f"Error al verificar el registro {registro}: {str(e)}")

    return listaIncompatibles  

        

   
