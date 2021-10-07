import cv2

classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cameraIP = cv2.VideoCapture(0) #WebCam
#cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.101/') #cameraIP

amostra = 1
numeroAmostras = 20
id = input('Digite seu identificador: ')
largura, altura = 220, 220
print("Capturando as faces...")

while(True):
    conectado, imagem = cameraIP.read()

    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

    for (x, y, l, a) in facesDetectadas:
        cv2.rectangle(imagem, (x, y), (x + l, y + a), (0, 0, 255), 2)
        if cv2.waitKey(1) & 0xFF == ord('q'): #tecla 'q' captura as fotos
            imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
            cv2.imwrite("fotos/pessoa." + str(id) + "." + str(amostra) + ".jpg", imagemFace)
            print("[Foto" + str(amostra) + " capturada com sucesso]")
            amostra += 1

    cv2.imshow("Face", imagem)
    cv2.waitKey(1)
    if (amostra >= numeroAmostras + 1):
        break

print("Faces capturadas com sucesso!")
cameraIP.release()
cv2.destroyAllWindows()
