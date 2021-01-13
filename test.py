import requests
import cv2
import base64
import json
import time
from pprint import pprint

# client_id 为官网获取的AK， client_secret 为官网获取的SK
client_id = 'LnzH53Z0NG5Xl4CIWb2CaVfm'
client_secret = 'pepQwRV7xWL7CQI5ETrlwi1rBxjBsG1N'

host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
    client_id, client_secret)
response = requests.get(host)

status = 0
request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
paramsDict = {
    'image': '',
    'image_type': 'BASE64',
    'group_id_list': '402',
    'liveness_control': 'NORMAL'
}

if response:
    print('access_token为：' + response.json()['access_token'])
    print('expires_in为：', response.json()['expires_in'])
    access_token = response.json()['access_token']
    expires_in = response.json()['expires_in']
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}

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
    image = img.copy()
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

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)

        if x < 106 and x + w > 533 and y < 80 and y + h > 400 and w * h > 900:
            continue
        if not status:
            status += 1
            cv2.putText(img, 'detect a face', (10, 30),
                        cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                        0.8, (255, 255, 255), 2)
            break
        elif status == 1:
            status += 1
            cv2.putText(img, 'detect a face', (10, 30),
                        cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                        0.8, (255, 255, 255), 2)
            break

        cv2.putText(img, 'detecting', (10, 30),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                    0.8, (255, 255, 255), 2)

        base64_str = cv2.imencode('.jpg', image)[1].tobytes()
        base64_str = str(base64.b64encode(base64_str), encoding='utf-8')

        paramsDict['image'] = base64_str
        params = json.dumps(paramsDict)
        # print(params)

        response = requests.post(request_url, data=params, headers=headers)
        if response:
            pprint(response.json())
            if response.json()['error_code']:
                print(response.json()['error_code'])
                pprint(response.json())
            else:
                pprint(response.json())
                if 'result' in response.json():
                    for key in response.json()['result']['user_list']:
                        if key['score']<90:
                            continue
                        print('hello {},置信度:{}'.format(key['user_id'],key['score']))
                        status = -1
                break

        else:
            print('no response')
        cv2.imshow('image', image)

    cv2.imshow('img', img)
    if cv2.waitKey(30) == 27 or status == -1:
        break
