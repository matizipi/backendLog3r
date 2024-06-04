from bson import ObjectId
from mongoDB import db




def getLicenses():
    collection = db['licencias']
    cursor = collection.find()
    licenses = list(cursor)
    
    # Convertir ObjectId a cadena para que sea serializable
    for license in licenses:
        license['_id'] = str(license['_id'])
        license['userId'] = str(license['userId'])        
    
    return licenses

def newLicense(userId,fechaDesde,fechaHasta):
    collection = db['licencias']
    collection.insert_one({
        "fechaDesde": fechaDesde,
        "fechaHasta": fechaHasta,
        "userId":  ObjectId(userId)})   