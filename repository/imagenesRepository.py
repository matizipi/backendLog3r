from datetime import datetime

from database.connection import db
from bson import ObjectId

def get_image_embeddings():
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['imagenes']
    cursor = collection.find({})
    return cursor

def get_imagenes_repository(user_id):
    collection = db['imagenes']
    result = collection.find(
        {
            "userId": ObjectId(user_id)
        }
    )
    imagenes = list(result)
    for imagen in imagenes:
        imagen['_id'] = str(imagen['_id'])
        imagen['userId'] = str(imagen['userId'])

    return imagenes


def post_imagenes_repository(embedding, user_id):

    collection = db['imagenes']
    result = collection.insert_one({
        "embedding": embedding,
        "userId": ObjectId(user_id),
        "fecha": datetime.today().replace(microsecond=0)
    })

    result = {
        "_id": str(result.inserted_id),
        "embedding": embedding,
        "userId": user_id
    }

    return result

def put_imagenes_repository(_id, embedding, user_id):

    collection = db['imagenes']
    result = collection.update_one(
        {
        "_id": ObjectId(_id)
        },
        {"$set":
            {
            "embedding": embedding,
            "userId": ObjectId(user_id)
            }
        }
    )

    result = {
        "modifiedCount": result.modified_count
    }

    return result

def delete_imagenes_repository(_id):

    collection = db['imagenes']
    result = collection.delete_one(
        {
        "_id": ObjectId(_id)
        }
    )

    result = {
        "deletedCount": result.deleted_count
    }

    return result

