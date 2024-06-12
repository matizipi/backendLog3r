import os
import signal
import subprocess
import sys

from dotenv import load_dotenv

import utils
load_dotenv()

from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
from database.connection import client
from repository.eventosRepository import post_eventos_repository
from repository.licenciasRepository import getUserLicenses

import comparacionCaras
from api.imagenesApi import imagenes_bp
from api.licenciasApi import licencias_bp
from api.profesoresApi import profesores_bp
from api.logsApi import logs_bp
from api.rolesApi import roles_bp
from api.configApi import config_bp
from api.usersApi import users_bp
from api.horariosApi import horarios_bp
from api.eventosApi import eventos_bp
from api.reportesApi import reportes_bp

app = Flask(__name__)
cors = CORS(app)

salida_automatica_subprocess = None
def signal_handler(sig, frame):
    print(sig)
    client.close()
    print(salida_automatica_subprocess)
    if salida_automatica_subprocess is not None:
        salida_automatica_subprocess.send_signal(signal.SIGINT)
    print('Server closed!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@app.route('/')
def home():
    return jsonify({'message': 'home'}), 200


app.register_blueprint(imagenes_bp)
app.register_blueprint(licencias_bp, url_prefix = '/api/licencias')
app.register_blueprint(profesores_bp, url_prefix = '/api/profesores')
app.register_blueprint(logs_bp, url_prefix = '/api/logs')
app.register_blueprint(roles_bp, url_prefix = '/api/roles')
app.register_blueprint(config_bp, url_prefix = '/api/config')
app.register_blueprint(users_bp, url_prefix = '/api/users')
app.register_blueprint(horarios_bp, url_prefix = '/api/horarios')
app.register_blueprint(eventos_bp, url_prefix = '/api/eventos')
app.register_blueprint(reportes_bp, url_prefix= '/api/reportes')

@app.route('/api/authentication', methods=['POST'])
def authentication():
    try:
        data = request.json  # JSON payload containing the array of floats
        embeddings = data.get('embeddings', [])  # Extract the array of floats from JSON payload

        user_finded = comparacionCaras.compararEmbeddingConDB(embeddings)
        if user_finded is None or user_finded == -1:
            return jsonify({'message': 'Autenticación fallida:Usuario No Registro'}), 401
        
        # validaciones de licencia y horarios
        user_licenses = getUserLicenses(user_finded['_id'])

        dt = datetime.now()
        fecha_actual = dt.date()
        # Validar si la fecha actual está en algún rango de horario
        
        for license in user_licenses:
            fecha_desde = datetime.strptime(license['fechaDesde'], '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(license['fechaHasta'], '%Y-%m-%d').date()

            if fecha_desde <= fecha_actual <= fecha_hasta:
                active_license = {
                    'fechaDesde': license['fechaDesde'],
                    'fechaHasta': license['fechaHasta'],
                }
                evento = post_eventos_repository(user_finded['_id'], active_license, tipo='licencia')
                print('Ingreso irregular por licencia. Evento creado')
                return jsonify({'message': 'Autenticación exitosa', 'data': user_finded})

        user_finded['horarios'].sort(key=(lambda horarios: horarios['tipo'])) # ordenar por lunes a viernes, y luego sabado
        
        ingreso_horario_invalido = True

        weekday = fecha_actual.weekday() # 0 = lunes, ..., 6 = domingo
        if weekday == 6:
            print('Ingreso irregular por día domingo')
            ingreso_horario_invalido = True
        else:
            i = 0
            if weekday < 5: # lunes a viernes
                if (len(user_finded['horarios']) > 0):
                    while user_finded['horarios'][i]['tipo'] == 'lunes a viernes':
                        horario_entrada = user_finded['horarios'][i]['horarioEntrada']
                        horario_salida = user_finded['horarios'][i]['horarioSalida']

                        if horarioValido(dt, horario_entrada, horario_salida):
                            ingreso_horario_invalido = False
                            break

                        i+=1
            else: # sabado
                while i <= len(user_finded['horarios']) - 1:
                    if user_finded['horarios'][i]['tipo'] == 'sabado':
                        horario_entrada = user_finded['horarios'][i]['horarioEntrada']
                        horario_salida = user_finded['horarios'][i]['horarioSalida']

                        if horarioValido(dt, horario_entrada, horario_salida):
                            ingreso_horario_invalido = False
                            break
                    i+=1
        
        if ingreso_horario_invalido:
            horarios_db = []
            for i in range(len(user_finded['horarios'])):
                horarios_db.append({
                    'horarioEntrada': user_finded['horarios'][i]['horarioEntrada'],
                    'horarioSalida': user_finded['horarios'][i]['horarioSalida'],
                    'tipo': user_finded['horarios'][i]['tipo'],
                    }
                )
            evento = post_eventos_repository(user_finded['_id'], horarios_db, tipo='horario')
            print('Ingreso irregular por horario. Evento creado')
            
        return jsonify({'message': 'Autenticación exitosa', 'data': user_finded})
    except RuntimeError as e:
        return jsonify({'message': e.args[0]}), 400
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = 'Error interno en el servidor: {}'.format(str(e))
        return jsonify({'error': mensaje_error}), 500


def horarioValido(dt_actual: datetime, horario_entrada: str, horario_salida: str):
    dt_local = utils.utcToArgentina(dt_actual)
    hora_entrada, minuto_entrada = utils.getHoraMinutoFromHorario(horario_entrada)
    hora_salida, minuto_salida = utils.getHoraMinutoFromHorario(horario_salida)

    dt_entrada = datetime(dt_local.year, dt_local.month, dt_local.day, (hora_entrada + 3) % 24, minuto_entrada)
    dt_salida = datetime(dt_local.year, dt_local.month, dt_local.day, (hora_salida + 3) % 24 , minuto_salida)

    if utils.utcToArgentina(dt_entrada) <= dt_local <= utils.utcToArgentina(dt_salida):
        return True
    else:
        return False


@app.route('/api/login', methods=['POST'])
def login2():
    data = request.json  # JSON payload containing the array of floats
    embeddings = data.get('embeddings', [])  # Extract the array of floats from JSON payload

    user_finded = comparacionCaras.compararEmbeddingConDB(embeddings)
    if user_finded is None or user_finded == -1:
        return jsonify({'message': 'Autenticación fallida:Usuario No Registro'}), 401

    if 'seguridad' in user_finded['rol'] or 'recursos humanos' in user_finded['rol'] or 'administrador' in user_finded['rol']:
        # validaciones de licencia y horarios
        user_licenses = getUserLicenses(user_finded['_id'])

        dt = datetime.now()
        fecha_actual = dt.date()
        # Validar si la fecha actual está en algún rango de horario
        
        for license in user_licenses:
            fecha_desde = datetime.strptime(license['fechaDesde'], '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(license['fechaHasta'], '%Y-%m-%d').date()

            if fecha_desde <= fecha_actual <= fecha_hasta:
                active_license = {
                    'fechaDesde': license['fechaDesde'],
                    'fechaHasta': license['fechaHasta'],
                }
                evento = post_eventos_repository(user_finded['_id'], active_license, tipo='licencia')
                print('Ingreso irregular por licencia. Evento creado')
                return jsonify({'message': 'Autenticación exitosa', 'data': user_finded})
        
        user_finded['horarios'].sort(key=(lambda horarios: horarios['tipo'])) # ordenar por lunes a viernes, y luego sabado
        
        ingreso_horario_invalido = True

        weekday = fecha_actual.weekday() # 0 = lunes, ..., 6 = domingo
        if weekday == 6:
            print('Ingreso irregular por día domingo')
            ingreso_horario_invalido = True
        else:
            i = 0
            if weekday < 5: # lunes a viernes
                if (len(user_finded['horarios']) > 0):
                    while user_finded['horarios'][i]['tipo'] == 'lunes a viernes':
                        horario_entrada = user_finded['horarios'][i]['horarioEntrada']
                        horario_salida = user_finded['horarios'][i]['horarioSalida']

                        if horarioValido(dt, horario_entrada, horario_salida):
                            ingreso_horario_invalido = False
                            break

                        i+=1
            else: # sabado
                while i <= len(user_finded['horarios']) - 1:
                    if user_finded['horarios'][i]['tipo'] == 'sabado':
                        horario_entrada = user_finded['horarios'][i]['horarioEntrada']
                        horario_salida = user_finded['horarios'][i]['horarioSalida']

                        if horarioValido(dt, horario_entrada, horario_salida):
                            ingreso_horario_invalido = False
                            break
                    i+=1
        
        if ingreso_horario_invalido:
            horarios_db = []
            for i in range(len(user_finded['horarios'])):
                horarios_db.append({
                    'horarioEntrada': user_finded['horarios'][i]['horarioEntrada'],
                    'horarioSalida': user_finded['horarios'][i]['horarioSalida'],
                    'tipo': user_finded['horarios'][i]['tipo'],
                    }
                )
            evento = post_eventos_repository(user_finded['_id'], horarios_db, tipo='horario')
            print('Ingreso irregular por horario. Evento creado')

        return jsonify({'message': 'Autenticación exitosa', 'data': user_finded})

    return jsonify({'message': 'Rol incorrecto'}), 401

    
def launch_script_automatic_log():
    # Lanza el script salidaAutomatica.py en segundo plano
    global salida_automatica_subprocess
    salida_automatica_subprocess = subprocess.Popen(['python', 'salidaAutomatica.py'])


if __name__ == '__main__':
    # development
    # launch_script_automatic_log()
    port = os.getenv('PORT', 5000)  # provided by Railway
    app.run(host='0.0.0.0', port=port, debug=True)


def deploy_server():
    # production
    launch_script_automatic_log()
    port = os.getenv('PORT')  # provided by Railway
    serve(app, host='0.0.0.0', port=port)
