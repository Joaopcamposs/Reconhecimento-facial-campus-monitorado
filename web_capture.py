import cv2
import numpy as np
from sqlalchemy.orm import Session
from database import get_db
from crud import pegar_camera_por_id, CameraNaoExiste, criar_pessoa, pegar_todas_pessoas, \
    pegar_captura_por_id, resetar_foto_flag
from schema import AdicionarAtualizarPessoa


# Parametros para reconhecimento facial
classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
largura, altura = 220, 220


async def stream_cadastra_pessoa(session: Session, id_camera: int, nome_pessoa: str):
    amostra = 1
    numero_amostras = 20
    imagem = None
    camera = None

    # Pegar lista de pessoas e determinar proximo id
    with Session(get_db()) as session:
        id = len(pegar_todas_pessoas(session=session)) + 1
        session.commit()
    nome = nome_pessoa

    try:
        camera = pegar_camera_por_id(session=session, _id=id_camera)
        captura = pegar_captura_por_id(session=session, _id=1)
    except CameraNaoExiste:
        imagem = cv2.imread("camera_nao_existe.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", imagem)
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
    camera_ip = cv2.VideoCapture(f'rtsp://{camera.usuario}:{camera.senha}@{camera.ip_da_camera}/')
    # cameraIP = cv2.VideoCapture(0)  #Hardcoded WebCam
    if camera:
        while amostra <= numero_amostras:
            conectado, frame = camera_ip.read()
            if conectado:
                try:
                    imagem_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces_detectadas = classificador.detectMultiScale(imagem_cinza, scaleFactor=1.5, minSize=(150, 150))

                    for (x, y, l, a) in faces_detectadas:
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        cv2.putText(frame, f'Luminosidade (min:110): {str(int(np.average(imagem_cinza)))}', (x, y + (a + 30)),font, 1, (0, 0, 255))
                        # if cv2.waitKey(1) & 0xFF == ord('q'):  # tecla 'q' captura as fotos
                        if captura.salvar_foto == 1:
                            if np.average(imagem_cinza) > 110:  # captura apenas se a media de luminosidade for maior que 110
                                imagem_face = cv2.resize(imagem_cinza[y:y + a, x:x + l], (largura, altura))
                                cv2.imwrite("fotos/pessoa." + str(id) + "." + str(amostra) + ".jpg", imagem_face)
                                amostra += 1
                                resetar_foto_flag(session, 1)

                    cv2.imshow("Face", frame)
                    # Redimensionar imagem
                    (flag, encodedImage) = cv2.imencode(".jpg", frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
                except Exception as e:
                    print(e)
            session.commit()
            session.refresh(camera)
            session.refresh(captura)
            camera = pegar_camera_por_id(session=session, _id=id_camera)
            captura = pegar_captura_por_id(session=session, _id=1)
        cv2.destroyAllWindows()
        try:
            imagem = cv2.imread("camera_desligada.jpg")
            (flag, encodedImage) = cv2.imencode(".jpg", imagem)
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
        except Exception as e:
            print(e)

        # Adicionar nome e id da pessoa no banco apos a captura das imagens
        with Session(get_db()) as session:
            pessoa = AdicionarAtualizarPessoa(id_pessoa=int(id), nome=nome)
            pessoa = criar_pessoa(pessoa_info=pessoa, session=session)
