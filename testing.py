import cv2
import os
import numpy as np
import time

inicio = time.time()
ruta_script = os.path.abspath(__file__)
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_script))
faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
imageSize=(150,150)

##Para probar modelo con imagen
image = cv2.imread(os.path.join(ruta_proyecto,'rostrosParaTest/dibu-prueba.PNG'),0)
image = cv2.resize(image,imageSize,interpolation=cv2.INTER_CUBIC)
imageAux = image.copy()
face = faceClassif.detectMultiScale(image,1.1,5,cv2.CASCADE_SCALE_IMAGE,[30,30],[300,300])
# recorto y guardo las imagenes de los rostros
for (x,y,w,h) in face:
    image = cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
    rostro = imageAux[y:y+h,x:x+w]
    rostro = cv2.resize(rostro,imageSize,cv2.INTER_CUBIC)
LBPHrecognizer = cv2.face.LBPHFaceRecognizer.create()

LBPHrecognizer.read('modelo.xml')
result = LBPHrecognizer.predict(rostro)
print("EL RESULTADO ES :")
print(result)
fin = time.time()
duracion = fin - inicio
print("El proceso tomó", duracion, "segundos.")



