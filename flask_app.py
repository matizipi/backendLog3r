import cv2.data
from flask import Flask,jsonify,request
import cv2 
import numpy as np
import os
from .training import *
from .captureFace import * 
from mongoDB import searchMdb

ultimo_Label = 0

app = Flask(__name__)

@app.route('/')
def home():
    return 'home'
  
@app.route('/prueba')
def prueba():
    return 'Testeando la ruta nueva...'

@app.route('/api/authentication', methods=['POST'])
def predict():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    rostro = detectarRostro(image)
    LBPHrecognizer = cv2.face.LBPHFaceRecognizer.create()
    LBPHrecognizer.read('modelo.xml')
    label, accuracy = LBPHrecognizer.predict(rostro)
    if label ==-1:        
        jsonify({"message": "Autenticación fallida"}) 
    result = searchMdb(label)     
    return jsonify({"message": "Autenticación exitosa", "data": result})

## Para el proximo sprint 3" 
@app.route('/api/register', methods=['POST'])
def register():
    firebaceStorageVideo_url = request.json 
    captureFace(firebaceStorageVideo_url)
    return jsonify({'Exito': 'Usuario registrado'})


if __name__== "__main__":
    app.run(debug=True)

# if (os.path.exists('modelo.xml')):
#     # hacer algo si el archivo existe
#     pass    
# else:
#     # entrenar el modelo por primera vez    
#     training.train()



