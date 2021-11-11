import enum
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from banco_de_dados import Base


##================ CAMERAS ========================================================

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


##================ PESSOAS ========================================================

class Pessoas(Base):
    __tablename__ = "pessoas"
    id_pessoa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String)

