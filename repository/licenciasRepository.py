from bson import ObjectId
from mongoDB import db
from datetime import datetime




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
    

def deleteLicencia(user_id):
    collection = db['licencias']
    licencia = collection.find_one({'_id': ObjectId(user_id)})
    fechaDesde = datetime.strptime(licencia.fechaDesde, '%Y-%m-%d')     
    fecha_actual = datetime.now()
    # Formatear la fecha para obtener solo el año, mes y día
    fecha_de_hoy = fecha_actual.strftime('%Y-%m-%d')

    if licencia and fecha_de_hoy < fechaDesde:
        result = collection.delete_one({'_id': ObjectId(user_id)})
    return {'mensaje': 'Licencia eliminada' if result.deleted_count > 0 else 'Licencia no encontrado'}    