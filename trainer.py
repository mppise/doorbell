import numpy as np
import cv2
from PIL import Image

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

id = input('ID this face: ')
sample = 0

while(True):
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if(len(faces)!=0):
        for (x,y,w,h) in faces:
            sample = sample+1
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,255),1)
            cropped = gray[y:(y+h), x:(x+w)]
            cv2.imwrite('/home/pi/apps/sample/'+str(id)+'.'+str(sample)+'.jpg', cropped)
            print("Sample "+ str(sample) + " saved")
            cv2.waitKey(1000);
            
    cv2.imshow('image', cropped);
    if(sample > 5):
        break

cam.release()
cv2.destroyAllWindows()
