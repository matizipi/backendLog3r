import cv2.data
from flask import Flask,jsonify,request
import cv2 
import numpy as np
import os
#import captureFace,training 
from mongoDB import searchMdb
import comparacionCarasOffline
import json
from bson import json_util
## variable global para ir guardando el ultimo label usado en el modelo
ultimo_Label = 0


app = Flask(__name__)


@app.route('/')
def home():
    return 'home'


@app.route('/api/authentication', methods=['POST'])
def predict():
    file = request.files['image']
    # Convertir la imagen a un formato adecuado para el procesamiento
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    
    result=comparacionCarasOffline.compararConDB(image)
    if result ==-1:        
        return jsonify({"message": "Autenticación fallida"}),401
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
        return jsonify({"message": "Autenticación fallida"}),401
    
    if "seguridad" in result["rol"] or "recursos humanos" in result["rol"] or "administrador" in result["rol"] :
        result_serializable = json.loads(json_util.dumps(result))
        return jsonify({"message": "Autenticación exitosa", "data": result_serializable})
    
    return jsonify({"message": "Rol incorrecto"}),401
## Para el proximo sprint 3" 


@app.route('/api/register', methods=['POST'])
def register():
    return 


if __name__== "__main__":
    app.run(debug=True)



