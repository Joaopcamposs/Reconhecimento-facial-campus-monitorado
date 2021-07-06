import cv2
from fastapi.responses import StreamingResponse
from fastapi import FastAPI

#cameraIP = cv2.VideoCapture(0) #WebCam
cameraIP = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.107/') #CameraIP

app = FastAPI()

#comando para iniciar a API
#uvicorn teste_web:app --reload


async def stream_camera_ip():
    while True:
        _, frame = cameraIP.read()
        frameResized = cv2.resize(frame, (720, 480), interpolation=cv2.INTER_AREA)
        (flag, encodedImage) = cv2.imencode(".jpg", frameResized)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
           bytearray(encodedImage) + b'\r\n')

@app.get("/video")
async def read_root():
    return StreamingResponse(stream_camera_ip(),  media_type="multipart/x-mixed-replace;boundary=frame")