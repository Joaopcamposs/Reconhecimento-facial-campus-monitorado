import cv2
from fastapi.responses import StreamingResponse
from fastapi import FastAPI

detectorFace = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.read("classificadorLBPH.yml")
largura, altura = 220, 220
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#cameraIP = cv2.VideoCapture(0) #WebCam
cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.107/') #CameraIP

#comando para iniciar a API
# uvicorn web:app --reload

app = FastAPI()

async def stream_camera_ip():
    while True:
        conectado, frame = cameraIP.read()

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

@app.get("/video")
async def read_root():
    return StreamingResponse(stream_camera_ip(), media_type="multipart/x-mixed-replace;boundary=frame")