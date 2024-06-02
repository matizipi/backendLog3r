from mongoDB import db
from bson import ObjectId


def get_usuario_repository(user_id):
    collection = db['usuarios']
    result = collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )
    # Si el usuario existe cambiar id
    if result:
        result['_id'] = str(result['_id'])

    return result
