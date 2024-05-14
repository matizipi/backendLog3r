import os
from dotenv import load_dotenv
load_dotenv()
import cv2.data
from flask import Flask,jsonify,request
import cv2 
import numpy as np
#import captureFace,training 

from mongoDB import searchMdb,unionPersonaEspacios,registrarLog

import comparacionCarasOffline
import json
from bson import json_util
from waitress import serve
## variable global para ir guardando el ultimo label usado en el modelo
ultimo_Label = 0


app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "home"}),200

@app.route('/api/authentication', methods=['POST'])
def predict():
    file = request.files['image']
    # Convertir la imagen a un formato adecuado para el procesamiento
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    
    result=comparacionCarasOffline.compararConDB(image)
    if result ==-1:        
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}),401
    print(result["rol"])
    result_serializable = json.loads(json_util.dumps(result))
    
    return jsonify({"message": "Autenticación exitosa", "data": result_serializable})

@app.route('/api/login', methods=['POST'])
def login():
    file = request.files['image']
    # Convertir la imagen a un formato adecuado para el procesamiento
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    
    result=comparacionCarasOffline.compararConDB(image)
    if result ==-1:        
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}),401
    
    if "seguridad" in result["rol"] or "recursos humanos" in result["rol"] or "administrador" in result["rol"] :
        result_serializable = json.loads(json_util.dumps(result))
        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})
    
    return jsonify({"message": "Rol incorrecto"}),401
## Para el proximo sprint 3" 


@app.route('/api/register', methods=['POST'])
def register():
    return 

@app.route('/api/authentication/logs',methods=['POST'])
def logs():
    data = request.form
    mensaje = data.get('mensaje')
    horario = data.get('horario')
    dni = data.get('dni')
    try:
        resultado = registrarLog(mensaje,horario,dni) 
        return jsonify(resultado), 200
    except Exception as e:
        # Si se produce un error, devuelve un código de estado HTTP 500 y un mensaje de error
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500     

@app.route('/api/prueba', methods=['POST'])
def prueba():
    file = request.files['image']
    # Convertir la imagen a un formato adecuado para el procesamiento
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    
    result=comparacionCarasOffline.compararConDB(image)
    if result ==-1:        
        return jsonify({"message": "Autenticación fallida:Usuario No Registro"}),401
    
    lugares=unionPersonaEspacios(result["_id"])
    result_serializable = json.loads(json_util.dumps(result))
    lugares = json.loads(json_util.dumps(lugares))
    return jsonify({"message": "Autenticación exitosa", "data": result_serializable,"lugares":lugares})


if __name__== "__main__":
    # development
    app.run(host='0.0.0.0', port=5000, debug=True)

def deploy_server():
    # production
    port = os.getenv('PORT') # provided by Railway
    serve(app, host='0.0.0.0', port=port)