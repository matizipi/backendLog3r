from datetime import datetime,timedelta
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
import cv2.data
from flask import Flask, jsonify, request
import cv2
import numpy as np
#import captureFace,training 

from mongoDB import (
    searchMdb, 
    unionPersonaEspacios, 
    createUser, 
    updateUser, 
    deleteUser, 
    getUsers,
    notificarCorte
    
)

import comparacionCaras
import json
from bson import json_util
from waitress import serve
from api.imagenesApi import imagenes_bp
from api.licenciasApi import licencias_bp
from api.profesoresApi import profesores_bp
from api.logsApi import logs_bp
from api.rolesApi import roles_bp
from api.configApi import config_bp

## variable global para ir guardando el ultimo label usado en el modelo
ultimo_Label = 0

from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)


@app.route('/')
def home():
    return jsonify({"message": "home"}), 200


app.register_blueprint(imagenes_bp)
app.register_blueprint(licencias_bp, url_prefix = '/api/licencias')
app.register_blueprint(profesores_bp, url_prefix = '/api/profesores')
app.register_blueprint(logs_bp, url_prefix = '/api/logs')
app.register_blueprint(roles_bp, url_prefix = '/api/roles')
app.register_blueprint(config_bp, url_prefix = '/api/config')

@app.route('/api/authentication', methods=['POST'])
def predict():
    try:
        file = request.files['image']
        # Convertir la imagen a un formato adecuado para el procesamiento
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

        userFinded = comparacionCaras.compararConDB(image)
        file.close()
        if userFinded == -1:
            return jsonify({"message": "Autenticación fallida: Usuario No Registrado"}), 401
        user_con_lugares = unionPersonaEspacios(userFinded)
        result_serializable = json.loads(json_util.dumps(user_con_lugares))

        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        print(mensaje_error)
        return jsonify({'error': mensaje_error}), 500


@app.route('/api/authentication2', methods=['POST'])
def authentication2():
    try:
        data = request.json  # JSON payload containing the array of floats
        embeddings = data.get('embeddings', [])  # Extract the array of floats from JSON payload
        # print(embeddings)

        result = comparacionCaras.compararEmbeddingConDB(embeddings)
        if result == -1:
            return jsonify({"message": "Autenticación fallida:Usuario No Registro"}), 401
        # print(result["rol"])
        # result_serializable = json.loads(json_util.dumps(result))
        user_con_lugares = unionPersonaEspacios(result)
        result_serializable = json.loads(json_util.dumps(user_con_lugares))

        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500


@app.route('/api/login', methods=['POST'])
def login():
    file = request.files['image']
    # Convertir la imagen a un formato adecuado para el procesamiento
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    result = comparacionCaras.compararConDB(image)
    file.close()
    if result == -1:
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}), 401

    if "seguridad" in result["rol"] or "recursos humanos" in result["rol"] or "administrador" in result["rol"]:
        result_serializable = json.loads(json_util.dumps(result))
        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})

    return jsonify({"message": "Rol incorrecto"}), 401


@app.route('/api/login2', methods=['POST'])
def login2():
    data = request.json  # JSON payload containing the array of floats
    embeddings = data.get('embeddings', [])  # Extract the array of floats from JSON payload

    result = comparacionCaras.compararEmbeddingConDB(embeddings)
    if result == -1:
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}), 401

    if "seguridad" in result["rol"] or "recursos humanos" in result["rol"] or "administrador" in result["rol"]:
        result_serializable = json.loads(json_util.dumps(result))
        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})

    return jsonify({"message": "Rol incorrecto"}), 401



def launch_script_automatic_log():
    # Lanza el script salidaAutomatica.py en segundo plano
    process = subprocess.Popen(["python", "salidaAutomatica.py"])


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.form
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horariosEntrada = data.get('horariosEntrada')
        horariosSalida = data.get('horariosSalida')
        email = data.get('email')

        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        
        result = createUser(nombre, apellido, int(dni), rol, horariosEntrada, horariosSalida,email)
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.form
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horariosEntrada = data.get('horariosEntrada')
        horariosSalida = data.get('horariosSalida')
        email = data.get('email')
        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        result = updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida, email)
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500


@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = deleteUser(user_id)
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500
    

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        result = getUsers()
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

   
 

@app.route('/api/certeza', methods=['GET'])
def getCerteza():
    return comparacionCaras.getTHRESHOLD()


@app.route('/api/certeza', methods=['POST'])
def setCerteza():
    umbral = request.form.get("THRESHOLD")

    try:
        if (comparacionCaras.setTHRESHOLD(request.form.get("THRESHOLD"))):
            return "Cambio exitoso", 200
        return "Cambio denegado", 400
    except Exception as e:
        print(e)
        return "Error de entrada",500
    
@app.route('/api/authentication/cortes', methods=['POST'])
def notificar_cortes_conexion():
    data = request.form    
    horario_desconexion_str = data.get('horarioDesconexion')  
    horario_reconexion_str = data.get('horarioReconexion')  
    cantRegSincronizados = data.get('cantRegSincronizados')
    periodoDeCorte_str=data.get('periodoDeCorte')
    try:
      
        horarioDesconexion = datetime.strptime(horario_desconexion_str, '%Y-%m-%d %H:%M:%S')
        horarioReconexion = datetime.strptime(horario_reconexion_str, '%Y-%m-%d %H:%M:%S')

         # Convertir periodoDeCorte_str a timedelta
        periodoDeCorte_time = datetime.strptime(periodoDeCorte_str, '%H:%M:%S')
        periodoDeCorte = timedelta(hours=periodoDeCorte_time.hour, minutes=periodoDeCorte_time.minute, seconds=periodoDeCorte_time.second)

        result = notificarCorte(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte)

        return jsonify(result), 200
    
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500 
    


if __name__ == "__main__":
    # development
    # launch_script_automatic_log()
    port = os.getenv('PORT', 5000)  # provided by Railway
    app.run(host='0.0.0.0', port=port, debug=True)


def deploy_server():
    # production
    launch_script_automatic_log()
    port = os.getenv('PORT')  # provided by Railway
    serve(app, host='0.0.0.0', port=port)
