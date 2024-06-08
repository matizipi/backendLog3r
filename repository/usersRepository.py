from bson import ObjectId
from mongoDB import db, guardarHistorialUsuarios, guardarHistorialUsuariosConCambios, normalizarDatosEnLogs, notificarCambioDeTitularidad

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


def create_user_repository(nombre, apellido, dni, rol, horarios, email):
    collection = db['usuarios']
    # Buscar usuario por dni para corroborar si existe
    usuario_existente = collection.find_one({'$or': [{'dni': dni},{'email': email}]},)
    if usuario_existente:
        raise RuntimeError("El usuario ya existe en la base de datos con el id {}".format(usuario_existente['_id']))
    
    for i in range(len(horarios)):
        horarios[i] = ObjectId(horarios[i])

    new_user = {            
        'nombre': nombre,
        'apellido': apellido,
        'dni': int(dni),
        'rol': rol,
        'horarios': horarios,
        'email': email
    }
    response = collection.insert_one(new_user)
    new_user['_id'] = str(response.inserted_id)
    guardarHistorialUsuarios(nombre, apellido, dni, rol, horarios)
    return new_user


def update_user_repository(user_id, nombre, apellido, dni, rol, horarios, email):
    collection = db['usuarios']
    json_usuario_original = get_user_repository(user_id) #obtengo usuario antes de modificarse

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
        json_usuario_modificado = {
            '_id': user_id,
            'nombre': nombre,
            'apellido': apellido,
            'dni': int(dni),
            'rol': rol,
            'horarios': horarios,
            'email':email
        }      
        campos_modificados = guardarHistorialUsuariosConCambios(json_usuario_original,json_usuario_modificado)
        normalizarDatosEnLogs(json_usuario_original,campos_modificados)
        notificarCambioDeTitularidad(json_usuario_original,json_usuario_modificado)
    
    return { 'modifiedCount': result.modified_count }

def delete_user_repository(user_id):
    collection = db['usuarios']
    result = collection.delete_one({'_id': ObjectId(user_id)})
    return { 'deletedCount': result.deleted_count }

