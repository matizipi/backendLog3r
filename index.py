from datetime import datetime
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
import cv2.data
from flask import Flask,jsonify,request
import cv2 
import numpy as np
#import captureFace,training 

from mongoDB import (
    obtener_logs_dia_especifico,
    searchMdb, 
    unionPersonaEspacios, 
    registrarLog, 
    createUser, 
    updateUser, 
    deleteUser, 
    getUsers
)


import comparacionCarasOffline
import json
from bson import json_util,ObjectId
from waitress import serve 
## variable global para ir guardando el ultimo label usado en el modelo
ultimo_Label = 0
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "home"}),200

@app.route('/api/authentication', methods=['POST'])
def predict():
    try:
        file = request.files['image']
        # Convertir la imagen a un formato adecuado para el procesamiento
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        
        result=comparacionCarasOffline.compararConDB(image)
        file.close()
        if result ==-1:        
            return jsonify({"message": "Autenticación fallida:Usuario No Registro"}),401
        print(result["rol"])
        #result_serializable = json.loads(json_util.dumps(result))
        user = unionPersonaEspacios(result["_id"]).next()
        result_serializable = json.loads(json_util.dumps(user))

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
    
    result=comparacionCarasOffline.compararConDB(image)
    file.close()
    if result ==-1:        
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}),401
    
    if "seguridad" in result["rol"] or "recursos humanos" in result["rol"] or "administrador" in result["rol"] :
        result_serializable = json.loads(json_util.dumps(result))
        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})
    
    return jsonify({"message": "Rol incorrecto"}),401
## Para el proximo sprint 3" 

@app.route('/api/day/logs', methods=['GET'])
def get_logs():
    data = request.json      
    try:
        fecha = data.get('fecha')
        result = obtener_logs_dia_especifico(fecha)
        return result, 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

@app.route('/api/authentication/logs', methods=['POST'])
def logs():
    data = request.form    
    horario_str = data.get('horario')  # Assuming the date is passed as a string
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    dni = data.get('dni')
    estado = data.get('estado')
    tipo = data.get('tipo')
    
    try:
        # Convert string to datetime object
        horario = datetime.strptime(horario_str, '%Y-%m-%d %H:%M:%S')  # Adjust the format if necessary       
        
        # Now you can use horario as a datetime object in your registrarLog function
        resultado = registrarLog(horario,nombre,apellido,dni,estado,tipo) 
        
        return jsonify(resultado), 200
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

def launch_script_automatic_log():
    # Lanza el script salidaAutomatica.py en segundo plano
    process = subprocess.Popen(
        ["python", "salidaAutomatica.py"]
    )
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horariosEntrada = data.get('horariosEntrada')
        horariosSalida = data.get('horariosSalida')
        image = data.get('imagen')
        email = data.get('email')
        image_np = comparacionCarasOffline.obtener_imagen_desde_json(image)
        # Validar categorías
        #if rol not in ['Estudiante', 'Docente', 'No Docente', 'Seguridad']:
        #    return jsonify({"error": "Rol no válido"}), 400
        
        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        
        result = createUser(nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image_np,email)
        return jsonify(result), 201
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horariosEntrada = data.get('horariosEntrada')
        horariosSalida = data.get('horariosSalida')
        image = data.get('image')
        email = data.get('email')

        # Validar categorías
        if rol not in ['Estudiante', 'Docente', 'No Docente', 'Seguridad']:
            return jsonify({"error": "Rol no válido"}), 400
        
        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        
        result = updateUser(user_id, nombre, apellido, dni, rol, horariosEntrada, horariosSalida, image,email)
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


if __name__== "__main__":
    # development
    app.run(host='0.0.0.0', port=5000, debug=True)

def deploy_server():
    # production
    port = os.getenv('PORT') # provided by Railway    
    serve(app, host='0.0.0.0', port=port)