import numpy as np
import cv2,time,os

# -- Configurations -- #
SCREEN_W = 960
SCREEN_H = 720
HAR_CLAS = "haarcascade_frontalface_default.xml"
IMG_SIZE = 95

face_cascade = cv2.CascadeClassifier(HAR_CLAS)
cam = cv2.VideoCapture(0)
cam.set(3, SCREEN_W) # Width
cam.set(4, SCREEN_H) # Height

facenum = 0
working = 0
while(True):
    ret, img = cam.read()
    if(ret == False):
        print("Error: Camera is possibly disconnected or busy")
        break
    else:
        #- Skip this loop if already working on a face
        if(working > 0):
            cv2.imshow("Main Door", img)
            if(cv2.waitKey(250) & 0xFF == ord('q')):
                working = 0
                print("Face tracking resumed")
                continue
            working = working - 1
            if(working % 40 == 0):
                print("Face tracking is paused ...(for "+str(int(working / 4))+" seconds more)")
            continue

        #- Get Faces in the crowd, if any
        faces = face_cascade.detectMultiScale(img, 1.6, 6)
        if(len(faces)!=0):
            print("Psst! "+str(len(faces))+" peep(s) at the door!")
            for (x,y,w,h) in faces:
                print("Face#: "+str(facenum+1)+" of "+str(len(faces))+" | Width: "+str(w)+"")
                #- Disregard smaller sizes
                if(w < IMG_SIZE):
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2)
                else:
                    #- get image dimensions (with padding) and ensure it does not go out of bounds                    
                    top = y
                    left = x
                    height = 0
                    width = 0
                    if(y-(h*0.5) > 0):
                        top = y-(h*0.5)
                    if(x-(w*0.5) > 0):
                        left = x-(w*0.5)
                    if(y+h+(h*0.5) > SCREEN_H):
                        height = SCREEN_H - y+h+(h*0.5)
                    else:
                        height = y+h+(h*0.5)
                    if(x+w+(w*0.5) > SCREEN_W):
                        width = SCREEN_W - x+w+(w*0.5)
                    else:
                        width = x+w+(w*0.5)
                    imgcrop = img[top:height, left:width]
                    #- Sharpen image
                    imgsave = cv2.filter2D(imgcrop, -1, np.array([[0,0,0], [0,1,0], [0,0,0]]))
                    cv2.imwrite('/home/pi/apps/clicks/face_'+str(facenum)+'.jpg', imgsave)
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0), 4)
                    facenum = facenum+1
            cv2.imshow("Main Door", img)
            cv2.waitKey(25)
        
            if(len(faces) == facenum):
                print("Got all faces. Uploading for identification...")
                #- Uploading to AWS for Rekognition
                for f in range(0, facenum):
                    key = time.strftime("%Y%m%d_%H%M%S-")+str(f)+".jpg"
                    file = "@/home/pi/apps/clicks/face_"+str(f)+".jpg"
                    #os.system('curl -X POST https://s3.amazonaws.com/standbye -F "key='+key+'" -F "file='+file+'" -F "Content-Type=image/jpeg"')
                os.system("omxplayer -o local /home/pi/apps/Christmas-doorbell-melody.mp3")
                os.system("rm /home/pi/apps/clicks/*.jpg")
                working = 240
                facenum = 0
            else:
                facenum = 0

        cv2.imshow("Main Door", img)
        if(cv2.waitKey(25) & 0xFF == ord('q')):
            break

cam.release()
cv2.destroyAllWindows()
