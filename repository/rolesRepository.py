from mongoDB import db
from bson import ObjectId

def get_roles_repository(id):
    collection = db['roles']
    filter = {} if id is None else {"_id": ObjectId(id)}
    result = collection.find(filter)

    roles = list(result)
    result.close()

    for role in roles:
        role['_id'] = str(role['_id'])
    return roles


def post_roles_repository(role_name, lugares):
    collection = db['roles']
    result = collection.insert_one({
        "nombre": role_name,
        "lugares": lugares
    })

    new_role = {
        "_id": str(result.inserted_id),
        "nombre": role_name,
        "lugares": lugares
    }

    return new_role


def put_roles_repository(_id, new_role_name, new_lugares):
    collection = db['roles']
    result = collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set":{
            "nombre": new_role_name,
            "lugares": new_lugares
            }
        }
    )
    return { "modifiedCount": result.modified_count }


def delete_roles_repository(_id):
    collection = db['roles']
    result = collection.delete_one({"_id": ObjectId(_id)})
    return { "deleted_count": result.deleted_count }

