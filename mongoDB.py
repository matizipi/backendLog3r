from pymongo import MongoClient
import certifi

# Configuración de la conexión a MongoDB
MONGO_HOST = 'mongodb+srv://pp1-rf-user:q0cK1qe153bpS5I0@cluster.0zuctio.mongodb.net'
MONGO_PORT = 27017
MONGO_DB = 'pp1_rf'

# Crear una instancia de MongoClient
client = MongoClient(MONGO_HOST, MONGO_PORT,tlsCAFile=certifi.where())

# Obtener una referencia a la base de datos
db = client[MONGO_DB]

def searchMdb():
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['usuarios']    
    result = []
    filtro = {}
    cursor = collection.find(filtro)
    return cursor
    
def registrarLog(mensaje,horario,dni):
    # Realizar operaciones con la base de datos MongoDB
    # Por ejemplo, puedes obtener una colección y devolver algunos documentos
    collection = db['logs']    
    response = collection.insert_one({
        'horario':horario,
        'mensaje':mensaje,
        'dni':dni
    })
    result = {
        'id': str(response.inserted_id),
        'horario':horario,
        'mensaje':mensaje,
        'dni':dni
    }
    return result   


if __name__== "__main__":
   
    searchMdb()
    