from typing import List
from sqlalchemy.orm import Session
from models import Camera, Person, Controller
from schema import CreateUpdateCamera, CreateUpdatePerson


# Function to get list of cameras info
def get_all_cameras(session: Session) -> List[Camera]:
    return session.query(Camera).all()


class CameraNotFound(Exception):
    pass


# Function to get info of a particular camera
def get_camera_by_id(session: Session, _id: int) -> Camera:
    camera = session.query(Camera).get(_id)

    if camera is None:
        raise CameraNotFound

    return camera


# Function to add a new camera info to the database
def create_camera(session: Session, camera_info: CreateUpdateCamera) -> Camera:
    new_camera = Camera(**camera_info.dict())
    session.add(new_camera)
    session.commit()
    session.refresh(new_camera)
    return new_camera


# Function to update details of the camera
def update_camera(session: Session, _id: int, info_update: CreateUpdateCamera) -> Camera:
    camera = get_camera_by_id(session, _id)

    if camera is None:
        raise Exception

    camera.camera_ip = info_update.camera_ip
    camera.user = info_update.user
    camera.status = info_update.status
    camera.password = info_update.password
    session.commit()
    session.refresh(camera)

    return camera


# Function to delete a camera info from the db
def remove_camera(session: Session, _id: int):
    camera_info = get_camera_by_id(session, _id)

    if camera_info is None:
        raise Exception

    session.delete(camera_info)
    session.commit()

    return


# Function to get list of persons
def get_all_persons(session: Session) -> List[Person]:
    return session.query(Person).all()


class PersonNotFound(Exception):
    pass


# Function to get info of a particular person
def get_person_by_id(session: Session, _id: int) -> Person:
    pessoa = session.query(Person).get(_id)

    if pessoa is None:
        raise PersonNotFound

    return pessoa


# Function to add a new person info to the database
def create_person(session: Session, person_info: CreateUpdatePerson) -> Person:
    new_person = Person(**person_info.dict())
    session.add(new_person)
    session.commit()
    session.refresh(new_person)
    return new_person


# Function to update details of the person
def update_person(session: Session, _id: int, info_update: CreateUpdatePerson) -> Person:
    person = get_person_by_id(session, _id)

    if person is None:
        raise Exception

    person.person_id = info_update.person_id
    person.name = info_update.name
    session.commit()
    session.refresh(person)

    return person


# Function to delete a person from the db
def remove_person(session: Session, _id: int):
    person_info = get_person_by_id(session, _id)

    if person_info is None:
        raise Exception

    session.delete(person_info)
    session.commit()

    return


# Function to get info of a particular capture
async def get_capture_by_id(session: Session, _id: int) -> Controller:
    capture = session.query(Controller).get(_id)

    if capture is None:
        raise Exception

    return await capture


# Function to set captura flag
async def set_capture_flag(session: Session, _id: int):
    capture = await get_capture_by_id(session, _id)
    capture.save_picture = 1

    session.commit()
    session.refresh(capture)

    return await capture


# Function to reset captura flag
async def reset_capture_flag(session: Session, _id: int):
    capture = await get_capture_by_id(session, _id)
    capture.save_picture = 0

    session.commit()
    session.refresh(capture)

    return await capture


# Function to create database and tables
def create_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('mysql+pymysql://root:password@iftm_db/')
    Session = sessionmaker(engine)
    try:
        with Session.begin() as session:
            session.execute('CREATE DATABASE iftm;')
            session.execute('use iftm;')
            session.execute("""create table camera(
                            camera_id int auto_increment primary key,
                            user varchar(50),
                            camera_ip varchar(50),
                            password varchar(50),
                            status varchar(50)
                            );""")
            session.execute("""create table person(
                            person_id int auto_increment primary key,
                            name varchar(50)
                            );""")
            session.execute("""create table controller(
                            capture_id int primary key,
                            save_picture int
                            );""")
            session.execute("""insert into controller(capture_id, save_picture)
                            values (1, 0);""")
            session.commit()
    except:
        return "Something went wrong"

    return "Banco Criado"
