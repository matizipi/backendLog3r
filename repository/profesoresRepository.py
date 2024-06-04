from mongoDB import db


def getTeachers():
    collection = db['usuarios']
    cursor = collection.find({"rol":"profesor"})
    teachers = list(cursor)

    # Convertir ObjectId a cadena para que sea serializable
    for teacher in teachers:
        teacher['_id'] = str(teacher['_id'])

    return teachers



