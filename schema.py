from pydantic import BaseModel
from models import CameraStatus


class CreateUpdateCamera(BaseModel):
    user: str
    camera_ip: str
    password: str
    status: CameraStatus


class UpdateCamera(CreateUpdateCamera):
    id: int

    class Config:
        orm_mode = True


class CreateUpdatePerson(BaseModel):
    person_id: int
    name: str


class UpdatePerson(CreateUpdatePerson):
    person_id: int

    class Config:
        orm_mode = True
