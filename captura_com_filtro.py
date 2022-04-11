import cv2
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from crud import pegar_todas_pessoas, criar_pessoa
from schema import AdicionarAtualizarPessoa

classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
#cameraIP = cv2.VideoCapture(0) #WebCam
cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.101/') #cameraIP
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/iftm')

amostra = 1
numeroAmostras = 20

## Pegar lista de pessoas e determinar proximo id
with Session(engine) as session:
    id = len(pegar_todas_pessoas(session=session))+1
    session.commit()

print(f'ID: {id}')
nome = input(f'Nome e sobrenome: ')

largura, altura = 220, 220
print("Capturando as faces...")

## While(amostra<amostra atual)
while(True):
    ## todo alterar true para um retorno de uma rota rest, caso seja 1, captura a imagem e add no contador
    conectado, imagem = cameraIP.read()

    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    #print(np.average(imagemCinza)) #media de luminosidade
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

    for (x, y, l, a) in facesDetectadas:
        cv2.rectangle(imagem, (x, y), (x + l, y + a), (0, 0, 255), 2)
        cv2.putText(imagem, f'Luminosidade (min:110): {str(int(np.average(imagemCinza)))}', (x, y + (a + 30)), font, 1, (0, 0, 255))
        if cv2.waitKey(1) & 0xFF == ord('q'): #tecla 'q' captura as fotos
            if np.average(imagemCinza) > 110: #captura apenas se a media de luminosidade for maior que 110
                imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
                cv2.imwrite("fotos/pessoa." + str(id) + "." + str(amostra) + ".jpg", imagemFace)
                print("[Foto" + str(amostra) + " capturada com sucesso]")
                amostra += 1

    cv2.imshow("Face", imagem)
    cv2.waitKey(1)
    if (amostra >= numeroAmostras + 1):
        break

## Adicionar nome e id da pessoa no banco apos a captura das imagens
with Session(engine) as session:
    print('passou')
    pessoa = AdicionarAtualizarPessoa(id_pessoa=int(id), nome=nome)
    print(pessoa)
    pessoa = criar_pessoa(pessoa_info=pessoa, session=session)
    print(pessoa)

print("Faces capturadas com sucesso!")
cameraIP.release()
cv2.destroyAllWindows()
