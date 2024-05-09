import cv2
import os
import imutils
##el SDK de Firebase para Python
###import pyrebase

# Configuración de Firebase
config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "databaseURL": "YOUR_DATABASE_URL",
    "storageBucket": "YOUR_STORAGE_BUCKET"
}

'''firebase = pyrebase.initialize_app(config)
storage = firebase.storage()'''

def captureFace(VideoSrc):
    '''# URL del video en Firebase Storage
    video_url = VideoSrc

    # Descargar el video desde Firebase Storage
    video_data = storage.child(video_url+".mp4").download_as_string()  '''

    imageSize=(150,150)
    ruta_script = os.path.abspath(__file__)
    ruta_proyecto = os.path.dirname(os.path.dirname(ruta_script))
    datapath = os.path.join(ruta_proyecto, 'data')
    personName, extension = os.path.splitext(VideoSrc)
    personName=personName
    personaPath=os.path.join(datapath,personName)

    if not os.path.exists(personaPath):
        print("Carpeta Creada: "+personaPath)
        os.makedirs(personaPath)
    cap=cv2.VideoCapture(VideoSrc) ## <<<<<< aca va video_data
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
        ###cv2.imshow("frame",frame)

        k= cv2.waitKey(1)
        if k == 27 or count>=300:break
