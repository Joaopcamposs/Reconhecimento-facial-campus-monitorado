import enum
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from database import Base


class EstadoCamera(enum.Enum):
    ligado = enum.auto()
    desligado = enum.auto()


class Cameras(Base):
    __tablename__ = "cameras"
    id_da_camera = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String)
    ip_da_camera = Column(String)
    senha = Column(String)
    estado = Column(Enum(EstadoCamera))


class Pessoas(Base):
    __tablename__ = "pessoas"
    id_pessoa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String)


class ControleCaptura(Base):
    __tablename__ = "controle_captura"
    id_captura = Column(Integer, primary_key=True, index=True, autoincrement=True)
    salvar_foto = Column(Integer)
