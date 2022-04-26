from time import sleep
import cv2
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.responses import StreamingResponse
from database import get_db
from sqlalchemy.orm import Session
from web_capture import stream_cadastra_pessoa
from schema import AdicionarAtualizarCamera, AdicionarAtualizarPessoa
from crud import criar_camera, pegar_camera_por_id, pegar_todas_cameras, atualizar_camera, \
    deletar_camera, pegar_todas_pessoas, pegar_pessoa_por_id, atualizar_pessoa, criar_pessoa, \
    deletar_pessoa, salvar_foto_flag
from training import treinarLBPH
from web_recognition import stream_camera_ip

app = APIRouter()


# API endpoint to get info of a particular camera
@app.get("/camera/{camera_id}")
def pegar_info_camera(camera_id: int, session: Session = Depends(get_db)):
    try:
        camera_info = pegar_camera_por_id(session, camera_id)
        return camera_info
    except Exception as e:
        raise e


# API endpoint to update a existing camera info
@app.put("/camera/{camera_id}")
def atualizar_info_camera(camera_id: int, new_info: AdicionarAtualizarCamera, background_tasks: BackgroundTasks, session: Session = Depends(get_db), ):
    try:
        background_tasks.add_task(atualizar_camera, session,camera_id, new_info)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to get the list of cameras
@app.get("/cameras")
def listar_cameras(session: Session = Depends(get_db)):
    cameras = pegar_todas_cameras(session=session)

    return cameras


# API endpoint to add a camera to the database
@app.post("/camera")
def nova_camera(background_tasks: BackgroundTasks, nova_camera: AdicionarAtualizarCamera, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(criar_camera, session, nova_camera)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to delete a camera from the database
@app.delete("/camera/{camera_id}")
def delete_camera(background_tasks: BackgroundTasks, camera_id: int, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(deletar_camera, session, camera_id)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to get info of a particular pessoa
@app.get("/pessoa/{pessoa_id}")
def pegar_info_pessoa(pessoa_id: int, session: Session = Depends(get_db)):
    try:
        pessoa_info = pegar_pessoa_por_id(session, pessoa_id)
        return pessoa_info
    except Exception as e:
        raise e


# API endpoint to update a existing pessoa info
@app.put("/pessoa/{pessoa_id}")
def atualizar_info_pessoa(pessoa_id: int, new_info: AdicionarAtualizarPessoa, background_tasks: BackgroundTasks, session: Session = Depends(get_db), ):
    try:
        background_tasks.add_task(atualizar_pessoa, session,pessoa_id, new_info)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to get the list of pessoas
@app.get("/pessoas")
def listar_pessoas(session: Session = Depends(get_db)):
    pessoas = pegar_todas_pessoas(session=session)

    return pessoas


# API endpoint to add a pessoa to the database
@app.post("/pessoa")
def nova_pessoa(background_tasks: BackgroundTasks, nova_pessoa: AdicionarAtualizarPessoa, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(criar_pessoa, session, nova_pessoa)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to delete a car info from the data base
@app.delete("/pessoa/{pessoa_id}")
def delete_pessoa(background_tasks: BackgroundTasks, pessoa_id: int, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(deletar_pessoa, session, pessoa_id)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to train a new file of facial recognition
@app.get("/treinamento")
def treinar_reconhecimento():
    ## Chamada para gerar novo arquivo de reconhecimento treinado
    try:
        treinarLBPH()
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API endpoint to stream and catch pictures
@app.get("/capturarFotos/{id_camera}&{nome_pessoa}")
def capturar_fotos(id_camera: int, nome_pessoa: str, session: Session = Depends(get_db)):
    try:
        return StreamingResponse(stream_cadastra_pessoa(session=session, id_camera=id_camera, nome_pessoa=nome_pessoa),
                                 media_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        raise e


# API endpoint to catch the atual image to a picture
@app.post("/capturar")
def capturar(session: Session = Depends(get_db)):
    try:
        salvar_foto_flag(session, 1)
        return 200, "Requisicao rebecida"
    except Exception as e:
        raise e


# API endpoint to facial recognition stream
@app.get("/video/{id_camera}")
def reconhecimento_facial(id_camera: int, session: Session = Depends(get_db)):
    return StreamingResponse(stream_camera_ip(session=session, id_camera=id_camera),
                             media_type="multipart/x-mixed-replace;boundary=frame")


# API endpoint to start background cameras
@app.get("/iniciar_cameras")
def iniciar_cameras_background():
    camera_ip = cv2.VideoCapture("rtsp://joaop:Jp103266@192.168.0.109/")
    while True:
        tem_imagem, frame = camera_ip.read()
        if tem_imagem:
            print("rodando em background")
        sleep(30)
