from mongoDB import db

def get_config_repository(config_name):
    collection = db['configuraciones']
    filter = {} if config_name is None else {"nombre": config_name}
    result = collection.find(filter)

    configuraciones = list(result)
    result.close()

    for config in configuraciones:
        config['_id'] = str(config['_id'])

    return configuraciones


def post_config_repository(config_name, value):
    collection = db['configuraciones']

    try:
        result = collection.insert_one({
            "nombre": config_name,
            "valor": value
        })
    except Exception as e:
        raise RuntimeError('that config name already exists')

    new_config = {
        "_id": str(result.inserted_id),
        "nombre": config_name,
        "valor": value
    }

    return new_config


def put_config_repository(config_name, new_value):
    collection = db['configuraciones']
    result = collection.update_one(
        {"nombre": config_name},
        {"$set":{
            "valor": new_value
            }
        }
    )
    return { "modifiedCount": result.modified_count }


def delete_config_repository(config_name):
    collection = db['configuraciones']
    result = collection.delete_one({"nombre": config_name})
    return { "deleted_count": result.deleted_count }

