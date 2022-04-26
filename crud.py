from typing import List
from sqlalchemy.orm import Session
from models import Cameras, Pessoas, ControleCaptura
from schema import AdicionarAtualizarCamera, AdicionarAtualizarPessoa


# Function to get list of cameras info
def pegar_todas_cameras(session: Session) -> List[Cameras]:
    return session.query(Cameras).all()


class CameraNaoExiste(Exception):
    pass


# Function to get info of a particular camera
def pegar_camera_por_id(session: Session, _id: int) -> Cameras:
    camera = session.query(Cameras).get(_id)

    if camera is None:
        raise CameraNaoExiste

    return camera


# Function to add a new camera info to the database
def criar_camera(session: Session, camera_info: AdicionarAtualizarCamera) -> Cameras:
    camera_nova = Cameras(**camera_info.dict())
    session.add(camera_nova)
    session.commit()
    session.refresh(camera_nova)
    return camera_nova


# Function to update details of the camera
def atualizar_camera(session: Session, _id: int, info_update: AdicionarAtualizarCamera) -> Cameras:
    camera = pegar_camera_por_id(session, _id)

    if camera is None:
        raise Exception

    camera.ip_da_camera = info_update.ip_da_camera
    camera.usuario = info_update.usuario
    camera.estado = info_update.estado
    camera.senha = info_update.senha
    session.commit()
    session.refresh(camera)

    return camera


# Function to delete a camera info from the db
def deletar_camera(session: Session, _id: int):
    camera_info = pegar_camera_por_id(session, _id)

    if camera_info is None:
        raise Exception

    session.delete(camera_info)
    session.commit()

    return


# Function to get list of pessoas info
def pegar_todas_pessoas(session: Session) -> List[Pessoas]:
    return session.query(Pessoas).all()


class PessoaNaoExiste(Exception):
    pass


# Function to get info of a particular camera
def pegar_pessoa_por_id(session: Session, _id: int) -> Pessoas:
    pessoa = session.query(Pessoas).get(_id)

    if pessoa is None:
        raise PessoaNaoExiste

    return pessoa


# Function to add a new camera info to the database
def criar_pessoa(session: Session, pessoa_info: AdicionarAtualizarPessoa) -> Pessoas:
    pessoa_nova = Pessoas(**pessoa_info.dict())
    session.add(pessoa_nova)
    session.commit()
    session.refresh(pessoa_nova)
    return pessoa_nova


# Function to update details of the camera
def atualizar_pessoa(session: Session, _id: int, info_update: AdicionarAtualizarPessoa) -> Pessoas:
    pessoa = pegar_pessoa_por_id(session, _id)

    if pessoa is None:
        raise Exception

    pessoa.id_pessoa = info_update.id_pessoa
    pessoa.nome = info_update.nome
    session.commit()
    session.refresh(pessoa)

    return pessoa


# Function to delete a camera info from the db
def deletar_pessoa(session: Session, _id: int):
    pessoa_info = pegar_pessoa_por_id(session, _id)

    if pessoa_info is None:
        raise Exception

    session.delete(pessoa_info)
    session.commit()

    return


# Function to get info of a particular camera
def pegar_captura_por_id(session: Session, _id: int) -> ControleCaptura:
    captura = session.query(ControleCaptura).get(_id)

    if captura is None:
        raise Exception

    return captura


# Function to set captura flag
def salvar_foto_flag(session: Session, _id: int):
    captura = pegar_captura_por_id(session, _id)
    captura.salvar_foto = 1

    session.commit()
    session.refresh(captura)

    return captura


# Function to reset captura flag
def resetar_foto_flag(session: Session, _id: int):
    captura = pegar_captura_por_id(session, _id)
    captura.salvar_foto = 0

    session.commit()
    session.refresh(captura)

    return captura


# Function to create database and tables
def create_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('mysql+pymysql://root:password@iftm_db/')
    Session = sessionmaker(engine)
    with Session.begin() as session:
        session.execute('CREATE DATABASE iftm;')
        session.execute('use iftm;')
        session.execute("""create table cameras(
                        id_da_camera int auto_increment primary key,
                        usuario varchar(50),
                        ip_da_camera varchar(50),
                        senha varchar(50),
                        estado varchar(50)
                        );""")
        session.execute("""create table pessoas(
                        id_pessoa int auto_increment primary key,
                        nome varchar(50)
                        );""")
        session.execute("""create table controle_captura(
                        id_captura int,
                        salvar_foto int
                        );""")
        session.commit()

    return "Banco Criado"
