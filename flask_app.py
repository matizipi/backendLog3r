import cv2.data
from flask import Flask,jsonify,request
import cv2
from cv2 import face
import numpy as np
import os
from training import detectarRostro, train
from captureFace import captureFace
from mongoDB import searchMdb

print("CV2 version"+str(cv2.__version__))

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
    if rostro is None:
        return jsonify({"message": "No se pudo detectar un rostro en la imagen"})

    LBPHrecognizer = face.LBPHFaceRecognizer.create()
    LBPHrecognizer.read("/home/matizipi123/backendLog3r/modelos/haarcascade_frontalface_default.xml")

    try:
        label, accuracy = LBPHrecognizer.predict(rostro)
    except cv2.error as e:
        return jsonify({"message": f"Error durante la predicción: {e}"})
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

if (os.path.exists('modeloNuevo.xml')):
     # hacer algo si el archivo existe
     pass
else:
     # entrenar el modelo por primera vez
     train()



