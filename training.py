import cv2
import os
import cv2.data
import numpy as np

##rutas al proyecto
datapath = '/home/matizipi123/backendLog3r/data'
peopleList = os.listdir(datapath)
peopleList.sort() # para que le ande a Gabi
print("lista de personas: "+ str(peopleList))
faceClassifier=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
labels=[]
facesData=[]
label=0
imageSize=(150,150)
threshold = 85

##Para hacer el resize de las fotos
def detectarRostro(image):
    face=faceClassifier.detectMultiScale(image,1.3,5)
    output=0
    for(x,y,w,h) in face:
        rostro=image[y:y+h,x:x+w]
        output=cv2.resize(rostro,imageSize,interpolation=cv2.INTER_CUBIC)

    return output

def train():
    global label
    for nameDir in peopleList:
        personPath=os.path.join(datapath,nameDir)
        print("Leyendo imagen en directorio:"+personPath)
        personPaths = os.listdir(personPath)
        personPaths.sort()
        for fileName in personPaths:

            #Direccion de imagen
            dirImagen=personPath+"/"+fileName
            image=cv2.imread(dirImagen,0)
            print("Rostro "+dirImagen)
            imageResize=detectarRostro(image)


            #Agrego Label y facedata
            labels.append(label)
            facesData.append(image)

            #Muestro la imagen

            cv2.imshow("imagen",image)
            cv2.waitKey(10)
        label=label+1

    print(labels)
    face_recognizer=cv2.face.LBPHFaceRecognizer.create()

    face_recognizer.setThreshold(threshold)
    print("Entrenando..........")
    face_recognizer.train(facesData,np.array(labels))

    face_recognizer.write("modelo.xml")
    print("Modelo guardado.....")
    print(peopleList)

if __name__== "__main__":
    train()