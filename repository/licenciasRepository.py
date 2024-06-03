from bson import ObjectId
from mongoDB import db



def getLicenses():
    collection = db['licencias']
    cursor = collection.find()
    licences = list(cursor)
    
    # Convertir ObjectId a cadena para que sea serializable
    for licence in licences:
        licence['_id'] = str(licence['_id'])
    
    return licences

def newLicense(userId,fechaDesde,fechaHasta):
    collection = db['licencias']
    collection.insert_one({
        "fechaDesde": fechaDesde,
        "fechaHasta": fechaHasta,
        "userId":  ObjectId(userId)})   