import enum
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from database import Base


class CameraStatus(enum.Enum):
    on = enum.auto()
    off = enum.auto()


class Camera(Base):
    __tablename__ = "camera"
    camera_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user = Column(String)
    camera_ip = Column(String)
    password = Column(String)
    status = Column(Enum(CameraStatus))


class Person(Base):
    __tablename__ = "person"
    person_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)


class Controller(Base):
    __tablename__ = "controller"
    capture_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    save_picture = Column(Integer)
