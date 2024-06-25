from abc import ABC, abstractmethod
from datetime import datetime
from database.connection import db
from bson import ObjectId

from utils import utcToArgentina

def get_eventos_repository(fecha_desde, fecha_hasta):
    collection = db['eventos']
    result = collection.find({'timestamp':{'$gte':fecha_desde, '$lte':fecha_hasta}})

    eventos = list(result)
    result.close()

    for evento in eventos:
        evento['_id'] = str(evento['_id'])
        try:
            evento['userId'] = str(evento['userId'])
        except:
            pass
        mongoDate = evento['timestamp']
        evento['timestamp'] = datetime.strftime(utcToArgentina(mongoDate), '%Y-%m-%d %H:%M:%S')
        # evento['timestamp'] = datetime.strftime(mongoDate, '%Y-%m-%d %H:%M:%S')
    return eventos


def get_evento_repository(id):
    collection = db['eventos']
    result = collection.find_one({'_id': ObjectId(id)})

    if result:
        result['_id'] = str(result['_id'])
        try:
            result['userId'] = str(result['userId'])
        except:
            pass
        mongoDate = result['timestamp']
        result['timestamp'] = datetime.strftime(utcToArgentina(mongoDate), '%Y-%m-%d %H:%M:%S')
        # result['timestamp'] = datetime.strftime(mongoDate, '%Y-%m-%d %H:%M:%S')
    return result


class Event(ABC):
    def __init__(self, dt: datetime, tipo: str, guardia=None):
        self.timestamp = dt
        if tipo not in ['horario', 'licencia', 'sincronización offline', 'autenticación fallida']:
            raise RuntimeError('Tipo de evento inválido')
        self.tipo = tipo
        print(guardia)
        if guardia is not None: # cuando se usa /api/login no importa el guardia, pero si en /api/authentication
            self.guardia = guardia
    
    @abstractmethod
    def createDocumentDB(self):
        pass

    # @abstractmethod
    # def createEmailBody(self):
    #     pass
        

class HorarioEvent(Event):
    def __init__(self, dt: datetime, horarios, user, guardia=None):
        super().__init__(dt, 'horario', guardia)
        self.user = {
            'nombre': user['nombre'],
            'apellido': user['apellido'],
            'dni': user['dni'],
            'rol': user['rol'],
        }
        self.horarios = horarios

    def createDocumentDB(self):
        return {
            'user': self.user,
            'horarios': self.horarios
        }

class LicenciaEvent(Event):
    def __init__(self, dt: datetime, licenciaActiva, user, guardia=None):
        super().__init__(dt, 'licencia', guardia)
        self.user = {
            'nombre': user['nombre'],
            'apellido': user['apellido'],
            'dni': user['dni'],
            'rol': user['rol'],
        }
        self.licencia = licenciaActiva
    
    def createDocumentDB(self):
        return {
            'user': self.user,
            'licencia': self.licencia
        }
    
class SincronizacionOfflineEvent(Event):
    def __init__(self, dt: datetime, guardia, horario_desconexion, horario_reconexion,cant_reg_sincronizados,periodo_de_corte, incompatibles):
        super().__init__(dt, 'sincronización offline', guardia)
        self.horario_desconexion = horario_desconexion
        self.horario_reconexion = horario_reconexion
        self.cant_reg_sincronizados = cant_reg_sincronizados
        self.periodo_de_corte = periodo_de_corte
        self.incompatibles = incompatibles

    def createDocumentDB(self):
        return {
            'horarioDesconexion': self.horario_desconexion,
            'horarioReconexion': self.horario_reconexion,
            'cantRegSincronizados': self.cant_reg_sincronizados,
            'periodoDeCorte': self.periodo_de_corte,
            'incompatibles': self.incompatibles,
        }

class AutenticationFallidaEvent(Event):
    def __init__(self, dt: datetime, guardia, embeddings):
        super().__init__(dt, 'autenticación fallida', guardia)
        self.embeddings = embeddings
    
    def createDocumentDB(self):
        return {
            'userEmbeddings': self.embeddings
        }

def post_eventos_repository(event: Event):
    collection = db['eventos']

    new_evento_db = event.createDocumentDB()
    new_evento_db['timestamp'] = event.timestamp

    try:
        new_evento_db['guardia'] = event.guardia
    except:
        pass
    new_evento_db['tipo'] = event.tipo

    print(new_evento_db)

    result = collection.insert_one(new_evento_db)
    new_evento_db['_id'] = result.inserted_id

    return new_evento_db


def delete_eventos_repository(_id):
    collection = db['eventos']
    result = collection.delete_one({'_id': ObjectId(_id)})
    return { 'deleted_count': result.deleted_count }

