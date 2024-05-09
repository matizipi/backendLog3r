import cv2
import os
import cv2.data
import numpy as np
import time

##rutas al proyecto
datapath = '/home/matizipi123/backendLog3r/data'
peopleList = os.listdir(datapath)
peopleList.sort() # para que le ande a Gabi
print("lista de personas: "+ str(peopleList))
haarcascade_path = "/home/matizipi123/backendLog3r/modelos/haarcascade_frontalface_default.xml"
print("Path del cascade : "+ str(haarcascade_path))
faceClassifier=cv2.CascadeClassifier(haarcascade_path)
labels=[]
facesData=[]
label=0
imageSize=(150,150)
threshold = 85

##Para hacer el resize de las fotos
def detectarRostro(image):
    faces = faceClassifier.detectMultiScale(image, 1.3, 5)
    if len(faces) == 0:
        return None  # No se detectaron rostros

    for (x, y, w, h) in faces:
        rostro = image[y:y + h, x:x + w]
        resized = cv2.resize(rostro, imageSize, interpolation=cv2.INTER_CUBIC)
        return resized

    return None  # Por si acaso

def train():
    global label
    for nameDir in peopleList:
        personPath=os.path.join(datapath,nameDir)
        print("Leyendo imagen en directorio:"+personPath)
        personPaths = os.listdir(personPath)
        personPaths.sort()

        for fileName in personPaths:
            #Direccion de imagen
            dirImagen = os.path.join(personPath, fileName)
            image=cv2.imread(dirImagen,0)
            if image is None:
                print(f"No se pudo cargar la imagen en la ruta {dirImagen}")
                continue
            imageResize=detectarRostro(image)
            if imageResize is not None:
                continue

            #Agrego Label y facedata
            labels.append(label)
            facesData.append(imageResize)

            #Muestro la imagen
            cv2.waitKey(10)
        label=label+1

    if not facesData:
        print("Error: `facesData` está vacío.")
        return

    if not labels:
        print("Error: `labels` está vacío.")
        return

    if len(facesData) != len(labels):
        print("Error: `facesData` y `labels` tienen longitudes diferentes.")
        return

    print("labelsss", labels)
    print("Ejemplos de `facesData`:", facesData[:5])
    print("Ejemplos de `labels`:", labels[:5])

    for i, face in enumerate(facesData):
        if not isinstance(face, np.ndarray):
            print(f"Error: `facesData[{i}]` no es una matriz NumPy.")
            return
        if face.size == 0:
            print(f"Error: `facesData[{i}]` está vacío.")
            return
        if face.shape[0] <= 0 or face.shape[1] <= 0:
            print(f"Error: `facesData[{i}]` tiene dimensiones inválidas: {face.shape}")
            return

    face_recognizer=cv2.face.LBPHFaceRecognizer.create()

    face_recognizer.setThreshold(threshold)
    print("Entrenando..........")
    try:
        face_recognizer.train(facesData, np.array(labels))
        print("Entrenamiento exitoso.")
        face_recognizer.write("modeloNuevo.xml")
        print("Modelo guardado.....")
        print(peopleList)
    except cv2.error as e:
        print(f"Error durante el entrenamiento: {e}")

if __name__== "__main__":
    train()