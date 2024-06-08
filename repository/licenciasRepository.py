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
    result = collection.insert_one({
        "fechaDesde": fechaDesde,
        "fechaHasta": fechaHasta,
        "userId":  userId}) 
    idstr = str(result.inserted_id)    
    return {'licenciaId': idstr}   
    

def deleteLicencia(licencia_id):
    collection = db['licencias']
    licencia = collection.find_one({'_id': ObjectId(licencia_id)})

    if licencia:
        fechaDesde = datetime.strptime(licencia['fechaDesde'], '%Y-%m-%d')
        fecha_actual = datetime.now()
        # Formatear la fecha para obtener solo el año, mes y día
        fecha_de_hoy = fecha_actual.strftime('%Y-%m-%d')
        
        # Convertir fecha_de_hoy a objeto datetime para comparación
        fecha_de_hoy = datetime.strptime(fecha_de_hoy, '%Y-%m-%d')

        if fecha_de_hoy < fechaDesde:
            result = collection.delete_one({'_id': ObjectId(licencia_id)})
            return {'mensaje': 'Licencia eliminada' if result.deleted_count > 0 else 'Licencia no encontrada'}
        else:
            return {'mensaje': 'No se puede eliminar la licencia porque la fechaDesde es pasada'}
    else:
        return {'mensaje': 'Licencia no encontrada'}    