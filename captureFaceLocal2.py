import cv2
import os
import imutils

imageSize=(150,150)
personName="esteban"
dataPath="D:/Facultad/AAAAAAFacultad/UNGS/Ano 2024/Cuatrimestre 1/Proyecto Profesional I/TP Final/flask-backend-log3r/data"
personaPath=dataPath+"/"+personName

if not os.path.exists(personaPath):
    print("Carpeta Creada: "+personaPath)
    os.makedirs(personaPath)
cap=cv2.VideoCapture(personName+".mp4")
faceClassifier=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
count=0
while True:
    ret, frame=cap.read()
    if ret==False:break
    frame= imutils.resize(frame,width=640)
    image=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=faceClassifier.detectMultiScale(frame,1.3,5)
    copyFrame=frame.copy()
    
    for(x,y,w,h) in faces:
        rostro=copyFrame[y:y+h,x:x+w]
        rostro=cv2.resize(rostro,imageSize,interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(personaPath+"/rostro_{}.jpg".format(count),rostro)
        count=count+1
    cv2.imshow("frame",frame)
    
    k= cv2.waitKey(1)
    if k == 27 or count>=200:break

cap.release()
cv2.destroyAllWindows()

