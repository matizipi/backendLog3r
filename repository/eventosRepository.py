from datetime import datetime
from database.connection import db
from bson import ObjectId

from utils import utcToArgentina

def get_eventos_repository(fecha_desde, fecha_hasta):
    collection = db['eventos']
    result = collection.find({'timestamp':{'$gte':fecha_desde, '$lte':fecha_hasta}})

    eventos = list(result)
    result.close()

    for evento in eventos:
        evento['_id'] = str(evento['_id'])
        evento['userId'] = str(evento['userId'])
        mongoDate = evento['timestamp']
        evento['timestamp'] = datetime.strftime(utcToArgentina(mongoDate), '%Y-%m-%d %H:%M:%S')
        # evento['timestamp'] = datetime.strftime(mongoDate, '%Y-%m-%d %H:%M:%S')
    return eventos


def get_evento_repository(id):
    collection = db['eventos']
    result = collection.find_one({'_id': ObjectId(id)})

    if result:
        result['_id'] = str(result['_id'])
        result['userId'] = str(result['userId'])
        mongoDate = result['timestamp']
        result['timestamp'] = datetime.strftime(utcToArgentina(mongoDate), '%Y-%m-%d %H:%M:%S')
        # result['timestamp'] = datetime.strftime(mongoDate, '%Y-%m-%d %H:%M:%S')
    return result


def post_eventos_repository(user_id, horarios_o_licencia, tipo):
    collection = db['eventos']

    new_evento = {
        'userId': ObjectId(user_id),
        'timestamp': datetime.now(),
    }
    new_evento['tipo'] = tipo

    if tipo == 'horario':
        new_evento['horarios'] = horarios_o_licencia
    else: # tipo == 'licencia'
        new_evento['licencia'] = horarios_o_licencia

    result = collection.insert_one(new_evento)
    new_evento['_id'] = result.inserted_id

    return new_evento


def delete_eventos_repository(_id):
    collection = db['eventos']
    result = collection.delete_one({'_id': ObjectId(_id)})
    return { 'deleted_count': result.deleted_count }

