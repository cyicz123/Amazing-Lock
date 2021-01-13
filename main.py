# encoding:utf-8

import cv2
import threading
import time
import requests
import base64
import json
import logging
from queue import Queue

# client_id 为官网获取的AK， client_secret 为官网获取的SK
client_id = 'LnzH53Z0NG5Xl4CIWb2CaVfm'
client_secret = 'pepQwRV7xWL7CQI5ETrlwi1rBxjBsG1N'
access_token = ''
group_id_list = '402'  # 百度人脸库用户组
liveness_control = 'NORMAL'  # 活体检测级别

status = 0
face = Queue(3)
users = Queue(5)
frames= Queue(10)
net = threading.Event()
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(levelname)s %(thread)s %(message)s')

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class GetAccessToken(threading.Thread):
    def __init__(self, threadName='getAccessToken'):
        super(GetAccessToken, self).__init__(name=threadName)
        self.host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
            client_id, client_secret)
        self.startTime, self.expires_in = 0, 0

    def run(self):
        while True:
            self.end = time.time()
            if self.end - self.startTime > self.expires_in or not net.isSet():
                self.update_token()
                time.sleep(2)
            else:
                time.sleep(86400)

    def update_token(self):
        try:
            self.response = requests.get(self.host)
            if self.response:
                if 'access_token' in self.response.json():
                    logging.info('access_token为：{}'.format(self.response.json()['access_token']))
                    logging.info('expires_in为：{}'.format(self.response.json()['expires_in']))
                    global access_token
                    access_token = self.response.json()['access_token']
                    self.expires_in = self.response.json()['expires_in']
                    self.startTime = time.time()
                    net.set()
                else:
                    net.clear()
                    logging.warning('error:{},error_description'.format(self.response.json()['error'],
                                                                        self.response.json()['error_description']))
            else:
                net.clear()
                logging.warning('there is no response!')
        except:
            net.clear()
            logging.warning('No Internet Connection！')


class SerchFace(threading.Thread):
    def __init__(self, threadName='serchFace'):
        super(SerchFace, self).__init__(name=threadName)
        self.requestUrl = "https://aip.baidubce.com/rest/2.0/face/v3/search?access_token=" + access_token
        self.paramsDict = {
            'image': '',
            'image_type': 'BASE64',
            'group_id_list': group_id_list,
            'liveness_control': liveness_control
        }
        self.params = ''
        self.headers = {'content-type': 'application/json'}
        self.base64Str=''

    def img2base64(self):
        img = face.get()
        self.base64Byte = cv2.imencode('.jpg', img)[1].tobytes()
        self.base64Str = str(base64.b64encode(self.base64Byte), encoding='utf-8')

    def run(self):
        while True:
            if net.isSet():
                self.requestUrl = "https://aip.baidubce.com/rest/2.0/face/v3/search?access_token=" + access_token
                self.img2base64()
                self.paramsDict['image'] = self.base64Str
                self.params = json.dumps(self.paramsDict)
                response = requests.post(self.requestUrl, data=self.params, headers=self.headers)
                if response:
                    data = response.json()
                    if data['error_code']:
                        logging.warning('error_code:{},error_msg:{}'.format(data['error_code'], data['error_msg']))
                    else:
                        result = data['result']['user_list']
                        for user in result:
                            if user['score']<90:
                                logging.info('group_id:{}-user_id:{}-score:{}%'.format(user['group_id'],user['user_id'],user['score']))
                            else:
                                users.put({'group_id':user['group_id'],'user_id':user['user_id']})
                else:
                    logging.warning('there is no response!')
            else:
                net.wait()

class Pass(threading.Thread):
    def __init__(self, threadName='Pass'):
        super(Pass, self).__init__(name=threadName)
        self.user={}

    def run(self) -> None:
        while True:
            self.user=users.get()
            logging.info('group_id:{}-user_id:{}'.format(self.user['group_id'],self.user['user_id']))
            global status
            status=-1

class Draw(threading.Thread):
    def __init__(self,threadName='Draw'):
        super(Draw, self).__init__(name=threadName)

    def run(self) -> None:


if __name__ == '__main__':
    logging.info('Starting...')
    token = GetAccessToken()
    token.setDaemon(True)
    token.start()
    consumer = SerchFace()
    consumer.setDaemon(True)
    consumer.start()
    p=Pass()
    p.setDaemon(True)
    p.start()

    while True:
        frameList=[]
        ret, img = capture.read()
        frameList.append(img)
        image = img.copy()##
        frameList.append({'rectangle':[(106, 80), (533, 400), (255, 255, 255), 5]})
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
        flag = False
        for (x, y, w, h) in faces:
            flag=True
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
            if x < 106 and x + w > 533 and y < 80 and y + h > 400 and w * h < 900:
                status=0
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
            elif status >1 and status <5:
                face.put(image)
                status+=1
            if status==-1:
                cv2.putText(img, 'Verify successfully!', (10, 30),
                            cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                            0.8, (255, 255, 255), 1)


        cv2.imshow('img', img)
        if cv2.waitKey(30) == 27 :
            break
    logging.info('ending')

