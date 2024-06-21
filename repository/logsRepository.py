from datetime import datetime, timedelta
from database.connection import db

def registrarLog(horario,nombre,apellido,dni,estado,tipo):
    
    collection = db['logs']      
    response = collection.insert_one({
        'horario':horario,
        'nombre':nombre,
        'apellido':apellido,
        'dni':int(dni),
        'estado':estado,
        'tipo':tipo})    

    result = {
        'id': str(response.inserted_id),
        'horario':horario,
        'nombre':nombre,
        'apellido':apellido,
        'dni':int(dni),
        'estado':estado,
        'tipo':tipo
    }
    return result


def obtener_logs_dia_especifico(fecha):    
    collection = db['logs']
    
    # Convertir la fecha en un rango de inicio y fin del día
    fecha_inicio = datetime.combine(fecha, datetime.min.time())
    fecha_fin = fecha_inicio + timedelta(days=1)
    #print(f"Rango de fecha: {fecha_inicio} - {fecha_fin}")  # Depuración

    # Pipeline de agregación
    pipeline = [
        {
            '$match': {
                'horario': {
                    '$gte': fecha_inicio,
                    '$lt': fecha_fin
                }
            }
        },
        {
            '$project': {
                'horarios': 0  # Excluir el campo 'horarios' si existe
            }
        }
    ]

    
    try:
        # Ejecutar el pipeline
        resultados = list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"Error ejecutando el pipeline: {e}")
        return []
    
    # Convertir los resultados a un formato adecuado para JSON
    resultados_json = []
    for resultado in resultados:        
        resultado['_id'] = str(resultado['_id'])  # Convertir ObjectId a string
        if 'horarios' in resultado:
            del resultado['horarios']  # Eliminar 'horarios' del resultado final
        resultados_json.append(resultado)

    return resultados_json  # Devolver como una lista de diccionarios


