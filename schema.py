from pydantic import BaseModel
from models import EstadoCamera


##================ CAMERAS ========================================================

class AdicionarAtualizarCamera(BaseModel):
    usuario: str
    ip_da_camera: str
    senha: str
    estado: EstadoCamera

class AtualizarCamera(AdicionarAtualizarCamera):
    id: int
    class Config:
        orm_mode = True


##================ PESSOAS ========================================================

class AdicionarAtualizarPessoa(BaseModel):
    id_pessoa: int
    nome: str

class AtualizarPessoa(AdicionarAtualizarCamera):
    id_pessoa: int
    class Config:
        orm_mode = True