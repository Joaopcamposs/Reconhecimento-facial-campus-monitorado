import cv2
from crud import pegar_camera_por_id, pegar_todas_pessoas
from models import EstadoCamera
from sqlalchemy.orm import Session
from crud import CameraNaoExiste

# Parametros para reconhecimento facial
detectorFace = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.read("classificadorLBPH.yml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
largura, altura = 220, 220


def verificarPessoa(session: Session, id: int):
    # Puxar do banco todos os nomes e ids cadastrados
    pessoas = pegar_todas_pessoas(session=session)
    for p in pessoas:
        if id == p.id_pessoa:
            return p.nome


async def stream_camera_ip(session: Session, id_camera: int):
    imagem = None
    camera = None
    try:
        camera = pegar_camera_por_id(session=session, _id=id_camera)
    except CameraNaoExiste:
        imagem = cv2.imread("camera_nao_existe.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", imagem)
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
    camera_ip = cv2.VideoCapture(f'rtsp://{camera.usuario}:{camera.senha}@{camera.ip_da_camera}/')
    # cameraIP = cv2.VideoCapture(0)  #Hardcoded WebCam
    if camera:
        while camera.estado == EstadoCamera.ligado:
            conectado, frame = camera_ip.read()
            if conectado:
                try:
                    imagem_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces_detectadas = detectorFace.detectMultiScale(imagem_cinza, scaleFactor=1.5, minSize=(30, 30))
                    for (x, y, l, a) in faces_detectadas:
                        imagem_face = cv2.resize(imagem_cinza[y:y + a, x:x + l], (largura, altura))
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        id, confianca = reconhecedor.predict(imagem_face)

                        # Verificar pessoa
                        nome = verificarPessoa(session, id)

                        cv2.putText(frame, nome, (x, y + (a + 30)), font, 2, (0, 0, 255))
                        cv2.putText(frame, str(f'Confianca: {round(confianca, 2)}%'), (x, y + (a + 50)), font, 1,
                                    (0, 0, 255))
                    # Redimensionar imagem
                    frame_resized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
                    (flag, encodedImage) = cv2.imencode(".jpg", frame_resized)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
                except Exception as e:
                    print(e)
            session.commit()
            session.refresh(camera)
            camera = pegar_camera_por_id(session=session, _id=id_camera)
        cv2.destroyAllWindows()
        try:
            imagem = cv2.imread("camera_desligada.jpg")
            (flag, encodedImage) = cv2.imencode(".jpg", imagem)
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
        except Exception as e:
            print(e)
