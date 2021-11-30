import cv2
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Depends
import api
from time import sleep
from banco_de_dados import get_db
from crud import pegar_camera_por_id, pegar_todas_pessoas
from models import EstadoCamera
from sqlalchemy.orm import Session
from crud import CameraNaoExiste

##Definir api
app = FastAPI()
app.include_router(api.router)

##Parametros para reconhecimento facial
detectorFace = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.read("classificadorLBPH.yml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
largura, altura = 220, 220


# comando para iniciar o servidor da API
# uvicorn web:app --workers 4
# http://127.0.0.1:8000/docs


def verificarPessoa(session: Session, id: int):

    ## Puxar do banco todos os nomes e ids cadastrados
    pessoas = pegar_todas_pessoas(session=session)

    for p in pessoas:
        if id == p.id_pessoa:
            return p.nome


async def stream_camera_ip(session: Session, id_camera: int):
    #Estanciar camera ip e pegar enderco
    imagem = None
    camera = None
    try:
        camera = pegar_camera_por_id(session=session, _id=id_camera)
    except CameraNaoExiste:
        imagem = cv2.imread("camera_nao_existe.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", imagem)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
    #cameraIP = cv2.VideoCapture(f'rtsp://{camera.usuario}:{camera.senha}@{camera.ip_da_camera}/')
    cameraIP = cv2.VideoCapture(0)  #Hardcoded WebCam
    if camera:
        while camera.estado == EstadoCamera.ligado:
            conectado, frame = cameraIP.read()
            if conectado:
                try:
                    imagemCinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    facesDetectadas = detectorFace.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(30, 30))
                    for (x, y, l, a) in facesDetectadas:
                        imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        id, confianca = reconhecedor.predict(imagemFace)

                        ##Verificar pessoa
                        nome = verificarPessoa(session, id)

                        cv2.putText(frame, nome, (x, y + (a + 30)), font, 2, (0, 0, 255))
                        cv2.putText(frame, str(f'Confianca: {round(confianca, 2)}%'), (x, y + (a + 50)), font, 1,
                                    (0, 0, 255))
                    ##Redimensionar imagem
                    frameResized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
                    (flag, encodedImage) = cv2.imencode(".jpg", frameResized)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                except Exception as e:
                    print(e)
            session.commit()
            session.refresh(camera)
            camera = pegar_camera_por_id(session=session, _id=id_camera)
        cv2.destroyAllWindows()
        try:
            imagem = cv2.imread("camera_desligada.jpg")
            (flag, encodedImage) = cv2.imencode(".jpg", imagem)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        except Exception as e:
            print(e)


@app.get("/video/{id_camera}")
def read_root(id_camera:int,session: Session = Depends(get_db) ):
    return StreamingResponse(stream_camera_ip(session=session, id_camera=id_camera),  media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/iniciar_cameras")
def iniciar():
    camera_ip = cv2.VideoCapture("rtsp://joaop:Jp103266@192.168.0.102/")
    while True:
        tem_imagem, frame = camera_ip.read()
        if tem_imagem:
            print("rodando em background")
        sleep(30)