import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from crud import get_camera_by_id, CameraNotFound, create_person, get_all_persons, \
    get_capture_by_id, reset_capture_flag
from database import get_db
from schema import CreateUpdatePerson


# Parametros para reconhecimento facial
classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
width, height = 220, 220
engine = create_engine("mysql+pymysql://root:password@iftm_db/iftm")


async def stream_pictures_capture(session: Session, camera_id: int, person_name: str):
    sample = 1
    number_of_samples = 20
    image = None
    camera = None

    # Pegar lista de pessoas e determinar proximo id
    with Session(engine) as session:
        id = len(get_all_persons(session=session)) + 1
        session.commit()
    name = person_name

    try:
        camera = get_camera_by_id(session=session, _id=camera_id)
        capture = get_capture_by_id(session=session, _id=1)
    except CameraNotFound:
        image = cv2.imread("camera_nao_encontrada.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", image)
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
    camera_ip = cv2.VideoCapture(f'rtsp://{camera.user}:{camera.password}@{camera.camera_ip}/')
    # camera_ip = cv2.VideoCapture(0)  #Hardcoded WebCam
    if camera:
        while sample <= number_of_samples:
            connected, frame = camera_ip.read()
            if connected:
                try:
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    detected_faces = classifier.detectMultiScale(gray_image, scaleFactor=1.5, minSize=(150, 150))

                    for (x, y, l, a) in detected_faces:
                        cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)
                        cv2.putText(frame, f'Luminosidade (min:110): {str(int(np.average(gray_image)))}',
                                    (x, y + (a + 30)), font, 1, (0, 0, 255))
                        # if cv2.waitKey(1) & 0xFF == ord('q'):  # tecla 'q' captura as pictures
                        if capture.save_picture == 1:
                            if np.average(gray_image) > 110:  # captura se a media de luminosidade for maior que 110
                                face_image = cv2.resize(gray_image[y:y + a, x:x + l], (width, height))
                                cv2.imwrite("pictures/person." + str(id) + "." + str(sample) + ".jpg", face_image)
                                sample += 1
                                reset_capture_flag(session, 1)

                    cv2.imshow("Face", frame)
                    (flag, encodedImage) = cv2.imencode(".jpg", frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
                except Exception as e:
                    print(e)

            session.commit()
            session.refresh(camera)
            session.refresh(capture)

            camera = get_camera_by_id(session=session, _id=camera_id)
            capture = get_capture_by_id(session=session, _id=1)
        cv2.destroyAllWindows()
        try:
            image = cv2.imread("camera_desligada.jpg")
            (flag, encodedImage) = cv2.imencode(".jpg", image)
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
        except Exception as e:
            print(e)

        # Adicionar nome e id da pessoa no banco apos a captura das imagens
        with Session(engine) as session:
            person = CreateUpdatePerson(id_pessoa=int(id), nome=name)
            person = create_person(person_info=person, session=session)
