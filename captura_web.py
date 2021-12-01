import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from crud import pegar_camera_por_id, CameraNaoExiste, criar_pessoa, pegar_todas_pessoas, \
    pegar_captura_por_id, resetar_foto_flag
from schema import AdicionarAtualizarPessoa


##Parametros para reconhecimento facial
classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/iftm')
largura, altura = 220, 220


async def stream_cadastra_pessoa(session: Session, id_camera: int, nome_pessoa: str):
    amostra = 1
    numeroAmostras = 20
    imagem = None
    camera = None

    ## Pegar lista de pessoas e determinar proximo id
    with Session(engine) as session:
        id = len(pegar_todas_pessoas(session=session)) + 1
        session.commit()
    nome = nome_pessoa
    #print(id)

    try:
        camera = pegar_camera_por_id(session=session, _id=id_camera)
        captura = pegar_captura_por_id(session=session, _id=1)
    except CameraNaoExiste:
        imagem = cv2.imread("camera_nao_existe.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", imagem)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
    cameraIP = cv2.VideoCapture(f'rtsp://{camera.usuario}:{camera.senha}@{camera.ip_da_camera}/')
    #cameraIP = cv2.VideoCapture(0)  #Hardcoded WebCam
    if camera:
        while(amostra <= numeroAmostras):
            conectado, frame = cameraIP.read()
            if conectado:
                try:
                    imagemCinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

                    for (x, y, l, a) in facesDetectadas:
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        cv2.putText(frame, f'Luminosidade: {str(int(np.average(imagemCinza)))}', (x, y + (a + 30)),font, 1, (0, 0, 255))
                        #if cv2.waitKey(1) & 0xFF == ord('q'):  # tecla 'q' captura as fotos
                        if(captura.salvar_foto == 1):
                            if np.average(imagemCinza) > 110:  # captura apenas se a media de luminosidade for maior que 110
                                imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
                                cv2.imwrite("fotos/pessoa." + str(id) + "." + str(amostra) + ".jpg", imagemFace)
                                amostra += 1
                                resetar_foto_flag(session, 1)

                    cv2.imshow("Face", frame)
                    ##Redimensionar imagem
                    (flag, encodedImage) = cv2.imencode(".jpg", frame)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
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
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        except Exception as e:
            print(e)

        ## Adicionar nome e id da pessoa no banco apos a captura das imagens
        with Session(engine) as session:
            pessoa = AdicionarAtualizarPessoa(id_pessoa=int(id), nome=nome)
            pessoa = criar_pessoa(pessoa_info=pessoa, session=session)