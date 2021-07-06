import cv2

classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cameraIP = cv2.VideoCapture(0) #WebCam
#cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.107/') #cameraIP

while(True):
    conectado, imagem = cameraIP.read()

    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

    for(x, y, l, a) in facesDetectadas:
        cv2.rectangle(imagem, (x, y), (x+l, y+a), (0, 0, 255), 2)

    cv2.imshow("Face", imagem)
    cv2.waitKey(1)

cameraIP.release()
cv2.destroyAllWindows()
