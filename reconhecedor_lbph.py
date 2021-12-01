import cv2

detectorFace = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.read("classificadorLBPH.yml")
largura, altura = 220, 220
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#cameraIP = cv2.VideoCapture(0) #WebCam
cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.15.34/') #CameraIP

pessoas = dict([('1', 'Joao Pedro'), ('2', 'Carolina'), ('3', 'Lucas'), ('4', 'Juliana'), ('5', 'Gabriel')])

def verificarPessoa(id: int):
    return pessoas.get(str(id))

while (True):
    conectado, imagem = cameraIP.read()
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    facesDetectadas = detectorFace.detectMultiScale(imagemCinza,
                                                    scaleFactor=1.5,
                                                    minSize=(30,30))
    for (x, y, l, a) in facesDetectadas:
        imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
        cv2.rectangle(imagem, (x, y), (x + l, y + a), (0,0,255), 2)
        id, confianca = reconhecedor.predict(imagemFace)

        ##Verificar pessoa
        nome = verificarPessoa(id)

        cv2.putText(imagem, nome, (x,y +(a+30)), font, 2, (0,0,255))
        cv2.putText(imagem, str(f'Confianca: {round(confianca, 2)}%'), (x,y + (a+50)), font, 1, (0,0,255))

    imagem = cv2.resize(imagem, (1280, 720))  # altera tamanho da imagem exibida (usar para camera ip)
    cv2.imshow("Face", imagem)
    if cv2.waitKey(1) == ord('q'):
        break

cameraIP.release()
cv2.destroyAllWindows()