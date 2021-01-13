import cv2
import time

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
capture.set(cv2.CAP_PROP_FPS, 30)
print('摄像头为{}x{}，帧率为{}'.format(
    capture.get(cv2.CAP_PROP_FRAME_WIDTH),
    capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
    capture.get(cv2.CAP_PROP_FPS)))

while True:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    ret, img = capture.read()
    start = time.time()
    cv2.rectangle(img, (106, 80), (533, 400), (255, 255, 255), 5)
    cv2.putText(img, 'Please put your face in this frame.', (140, 70),
                cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                0.8, (255, 255, 255), 2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,
                                          scaleFactor=1.1,
                                          minNeighbors=5,
                                          minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
    end = time.time()

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)

        cv2.putText(img, 'time:{}'.format(end - start), (10, 20),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                    0.8, (255, 255, 255), 1)
    cv2.imshow('img', img)
    if cv2.waitKey(30) == 27:
        break
