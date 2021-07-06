import cv2

cap = cv2.VideoCapture('rtsp://joaop:Jp103266@192.168.0.107/')

while True:
    ret, frame = cap.read()
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()