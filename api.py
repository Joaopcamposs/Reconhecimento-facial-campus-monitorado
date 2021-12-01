from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.responses import StreamingResponse

from banco_de_dados import get_db
from sqlalchemy.orm import Session

# from captura_web import capturar_fotos
from captura_web import stream_cadastra_pessoa
from schema import AdicionarAtualizarCamera, AdicionarAtualizarPessoa
from crud import criar_camera, pegar_camera_por_id, pegar_todas_cameras, atualizar_camera, \
    deletar_camera, pegar_todas_pessoas, pegar_pessoa_por_id, atualizar_pessoa, criar_pessoa, \
    deletar_pessoa, salvar_foto_flag

##================ CAMERAS ========================================================
from treinamento import treinarLBPH

router = APIRouter()
@router.get("/camera/{camera_id}")
def pegar_camera_info(camera_id: int, session: Session = Depends(get_db)):
    try:
        camera_info = pegar_camera_por_id(session, camera_id)
        return camera_info
    except Exception as e:
        raise e


# API to update a existing car info
@router.put("/camera/{camera_id}")
def atualizar_camera_api(camera_id: int, new_info: AdicionarAtualizarCamera, background_tasks: BackgroundTasks, session: Session = Depends(get_db), ):
    try:
        background_tasks.add_task(atualizar_camera, session,camera_id, new_info)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e

@router.get("/cameras")
def listar_cameras(session: Session = Depends(get_db)):
    cameras = pegar_todas_cameras(session=session)

    return cameras


@router.post("/camera")
def nova_camera(background_tasks: BackgroundTasks, nova_camera: AdicionarAtualizarCamera, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(criar_camera, session, nova_camera)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API to delete a car info from the data base
@router.delete("/camera/{camera_id}")
def delete_camera(background_tasks: BackgroundTasks, camera_id: int, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(deletar_camera, session, camera_id)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


##================ PESSOAS ========================================================

@router.get("/pessoa/{pessoa_id}")
def pegar_pessoa_info(pessoa_id: int, session: Session = Depends(get_db)):
    try:
        pessoa_info = pegar_pessoa_por_id(session, pessoa_id)
        return pessoa_info
    except Exception as e:
        raise e


# API to update a existing car info
@router.put("/pessoa/{pessoa_id}")
def atualizar_pessoa_api(pessoa_id: int, new_info: AdicionarAtualizarPessoa, background_tasks: BackgroundTasks, session: Session = Depends(get_db), ):
    try:
        background_tasks.add_task(atualizar_pessoa, session,pessoa_id, new_info)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e

@router.get("/pessoas")
def listar_pessoas(session: Session = Depends(get_db)):
    pessoas = pegar_todas_pessoas(session=session)

    return pessoas


@router.post("/pessoa")
def nova_pessoa(background_tasks: BackgroundTasks, nova_pessoa: AdicionarAtualizarPessoa, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(criar_pessoa, session, nova_pessoa)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e


# API to delete a car info from the data base
@router.delete("/pessoa/{pessoa_id}")
def delete_pessoa(background_tasks: BackgroundTasks, pessoa_id: int, session: Session = Depends(get_db)):
    try:
        background_tasks.add_task(deletar_pessoa, session, pessoa_id)
        return 200, "Requisição recebida"
    except Exception as e:
        raise e

@router.get("/treinamento")
def treinar_reconhecimento():
    ## Chamada para gerar novo arquivo de reconhecimento treinado
    try:

        treinarLBPH()

        return 200, "Requisição recebida"
    except Exception as e:
        raise e

@router.get("/cadastrarPessoa/{id_camera}&{nome_pessoa}")
def cadastrar_pessoa(id_camera: int, nome_pessoa: str, session: Session = Depends(get_db)):
    try:
        return StreamingResponse(stream_cadastra_pessoa(session=session, id_camera=id_camera, nome_pessoa=nome_pessoa),
                                 media_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        raise e

@router.post("/capturarFoto")
def capturar_foto(session: Session = Depends(get_db)):
    try:
        salvar_foto_flag(session, 1)
        return 200, "Requisicao rebecida"
    except Exception as e:
        raise e