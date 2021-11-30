import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from crud import pegar_camera_por_id, CameraNaoExiste, criar_pessoa, pegar_todas_pessoas
from models import EstadoCamera


##Parametros para reconhecimento facial
from schema import AdicionarAtualizarPessoa

classificador = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/iftm')
largura, altura = 220, 220

amostra = 1
numeroAmostras = 20


async def stream_cadastra_pessoa(session: Session, id_camera: int):

    ## Pegar lista de pessoas e determinar proximo id
    with Session(engine) as session:
        id = len(pegar_todas_pessoas(session=session)) + 1
        session.commit()
    nome = input(f'Nome e sobrenome: ')

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
        #while(continuar_capturando and amostra<=numeroAmostras):
            conectado, frame = cameraIP.read()
            if conectado:
                try:
                    imagemCinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

                    for (x, y, l, a) in facesDetectadas:
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        cv2.putText(frame, f'Luminosidade: {str(int(np.average(imagemCinza)))}', (x, y + (a + 30)),font, 1, (0, 0, 255))
                        #if cv2.waitKey(1) & 0xFF == ord('q'):  # tecla 'q' captura as fotos
                            #if capturar_foto_flag
                            #if np.average(imagemCinza) > 110:  # captura apenas se a media de luminosidade for maior que 110
                                #imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
                                #cv2.imwrite("fotos/pessoa." + str(id) + "." + str(amostra) + ".jpg", imagemFace)
                                #print("[Foto" + str(amostra) + " capturada com sucesso]")
                                #amostra += 1
                                # desativar_captura_foto_flag_banco
                                # vc vai mandar o comando para desativar a flag  pelo crud(chamar o update) direto ou tentar fazer por backgroundTasks

                    cv2.imshow("Face", frame)
                    # if (amostra >= numeroAmostras + 1):
                    #     break

                    ##Redimensionar imagem
                    (flag, encodedImage) = cv2.imencode(".jpg", frame)
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

        ## Adicionar nome e id da pessoa no banco apos a captura das imagens
        with Session(engine) as session:
            pessoa = AdicionarAtualizarPessoa(id_pessoa=int(id), nome=nome)
            pessoa = criar_pessoa(pessoa_info=pessoa, session=session)