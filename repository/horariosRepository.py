from mongoDB import db
from bson import ObjectId

def get_horarios_repository():
    collection = db['horarios']
    result = collection.find()

    horarios = list(result)
    result.close()

    for role in horarios:
        role['_id'] = str(role['_id'])
    return horarios


def get_horario_repository(id):
    collection = db['horarios']
    result = collection.find_one({"_id": ObjectId(id)})

    if result:
        result['_id'] = str(result['_id'])
    return result


def post_horarios_repository(horario_entrada: str, horario_salida: str, tipo):
    collection = db['horarios']
        
    new_horario = {
        'horarioEntrada': horario_entrada,
        'horarioSalida': horario_salida,
        'tipo': tipo
    }

    result = collection.insert_one(new_horario)
    new_horario['_id'] = str(result.inserted_id)

    return new_horario


def put_horarios_repository(_id, new_horario_entrada, new_horario_salida, new_tipo):
    collection = db['horarios']
    result = collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set":{
            'horarioEntrada': new_horario_entrada,
            'horarioSalida': new_horario_salida,
            'tipo': new_tipo
          }
        }
    )
    return { "modifiedCount": result.modified_count }


def delete_horarios_repository(_id):
    collection = db['horarios']
    result = collection.delete_one({"_id": ObjectId(_id)})
    return { "deletedCount": result.deleted_count }

