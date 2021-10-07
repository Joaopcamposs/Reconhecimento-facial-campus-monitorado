import cv2
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from pydantic import BaseModel

detectorFace = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.read("classificadorLBPH.yml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#cameraIP = cv2.VideoCapture(0) #WebCam
largura, altura = 220, 220
cameraAtual = 0

# class Camera(BaseModel):
#     id_camera: int
#     ip: str
#     user: str
#     password: str

# {
#     "id_camera": 1,
#     "ip": "127.0.0.1:8000/",
#     "user": "joaop",
#     "password": "Jp103266"
# }

#escrever ligado no banco
with open('banco.txt', "w") as myfile:
    myfile.write('ligado')
#escrever 0 na camera
with open('camera.txt', "w") as myfile:
    myfile.write('rtsp://joaop:Jp103266@192.168.15.34')

#comando para iniciar a API
# uvicorn web_v2:app --workers 2
#http://127.0.0.1:8000/video

app = FastAPI()

async def stream_camera_ip():
    #Estanciar camera ip e pegar enderco
    cameraIP = cv2.VideoCapture(escolher_camera('camera'))
    while ler_arquivo('banco') == "ligado":
        conectado, frame = cameraIP.read()
        print(conectado)
        if conectado:
            greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            facesDetectadas = detectorFace.detectMultiScale(greyFrame,
                                                            scaleFactor=1.5,
                                                            minSize=(30, 30))
            for (x, y, l, a) in facesDetectadas:
                imagemFace = cv2.resize(greyFrame[y:y + a, x:x + l], (largura, altura))
                cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                id, confianca = reconhecedor.predict(imagemFace)
                nome = ""
                if id == 1:
                    nome = 'Joao Pedro'
                elif id == 2:
                    nome = 'Carolina'
                elif id == 3:
                    nome = 'Lucas'
                elif id == 4:
                    nome = 'Juliana'
                elif id == 5:
                    nome = 'Gabriel'
                else:
                    nome = 'Desconhecido'
                cv2.putText(frame, nome, (x, y + (a + 30)), font, 2, (0, 0, 255))
                cv2.putText(frame, str(confianca), (x, y + (a + 50)), font, 1, (0, 0, 255))

            frameResized = cv2.resize(frame, (720, 480), interpolation=cv2.INTER_AREA)

            (flag, encodedImage) = cv2.imencode(".jpg", frameResized)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')
    cv2.destroyAllWindows()


#Requisicoes Web
@app.get('/video')
async def read_root():
    return StreamingResponse(stream_camera_ip(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post('/parar')
async def desligar_camera():
    escrever_banco('banco', 'desligado')
    return {"result": "Camera desligada"}

@app.post('/ligar')
async def ligar_camera():
    escrever_banco('banco', "ligado")
    return {"result": "Camera quase ligada"}

class CameraEscolher(BaseModel):
    camera: int

@app.post("/escolher")
async def escolher(camera: CameraEscolher):
    numero_camera = camera.camera
    escrever_banco('banco', 'desligado')

    if numero_camera == 0:
        escrever_banco('camera', 'rtsp://joaop:Jp103266@192.168.15.34')
    elif numero_camera == 1:
        escrever_banco('camera', '0')

    escrever_banco('banco', 'ligado')

    return {"result": "Requisicao recebida"}

def ler_arquivo(nome: str)-> str:
    data = ""
    with open(f'{nome}.txt', "r") as myfile:
        data = myfile.read()
        return data

def escrever_banco(nome: str, dado: str):
    with open(f'{nome}.txt', "w") as myfile:
        myfile.write(dado)

def escolher_camera(nome: str) -> str:
    data = ""
    with open(f'{nome}.txt', "r") as myfile:
        data = myfile.read()
        if data == '0':
           data = 0
        return data