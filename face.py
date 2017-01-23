import numpy as np
import cv2
from PIL import Image
import time
import os

# -- Configurations -- #
HAR_CLAS = "haarcascade_frontalface_alt.xml"
IMG_SIZE = 95
IMG_QUAL = 150

face_cascade = cv2.CascadeClassifier(HAR_CLAS)
cam = cv2.VideoCapture(0)
cam.set(3, 1280)    # Width
cam.set(4, 960)     # Height
cam.set(5, 30)      # FPS

facenum = 0
while(True):
    ret, img = cam.read()
    if(ret == False):
        print("Error: Camera is possibly disconnected or busy")
        break
    else:
        imgquality = int(cv2.Laplacian(img, cv2.CV_64F).var())

        #- Get Faces in the crowd, if any
        faces = face_cascade.detectMultiScale(img, 1.6, 6)
        
        if(len(faces)!=0):
            peeps = "person"
            if(len(faces)>1):
                peeps = "people"
            message = "Psst! "+str(len(faces))+" "+ peeps +" at the door!"
            print(message)
            for (x,y,w,h) in faces:
                print("Face#: "+str(facenum+1)+" of "+str(len(faces))+" | Width: "+str(w)+" | Quality: "+str(imgquality)+"")
                #- Disregard smaller sizes
                if(w < IMG_SIZE):
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2)
                else:
                    #- Checking quality of faces
                    if(imgquality < IMG_QUAL):
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255), 2)
                    else:
                        imgcrop = img[y-(h*0.5):(y+h+(h*0.5)), x-(w*0.5):(x+w+(w*0.5))]
                        cv2.imwrite('/home/pi/apps/clicks/face_'+str(facenum)+'.jpg', imgcrop)
                        facenum = facenum+1
        
            if(len(faces) == facenum):
                print("Got all faces. Uploading for identification...")
                #- Uploading to AWS for Rekognition
                for f in range(0, facenum):
                    key = time.strftime("%Y%m%d_%H%M%S-")+str(f)+".jpg"
                    file = "@/home/pi/apps/clicks/face_"+str(f)+".jpg"
                    #os.system('curl -X POST https://s3.amazonaws.com/standbye -F "key='+key+'" -F "file='+file+'" -F "Content-Type=image/jpeg"')
                os.system("omxplayer -o local /home/pi/apps/Christmas-doorbell-melody.mp3")
                #- start of idle loop
                for i in range(0, 240):
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.6, 6)
                    for (x,y,w,h) in faces:
                        cv2.rectangle(gray,(x,y),(x+w,y+h),(255,255,255), 2)
                    cv2.imshow("Main Door", gray)
                    cv2.waitKey(250)
                #- end of idle loop
                os.system("rm /home/pi/apps/clicks/*.jpg")
                facenum = 0
            else:
                facenum = 0

        cv2.imshow("Main Door", img)
        if(cv2.waitKey(25) & 0xFF == ord('q')):
            break

cam.release()
cv2.destroyAllWindows()
