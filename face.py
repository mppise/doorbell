import numpy as np
import cv2,time,os,requests,json

# -- Configurations -- #
SCREEN_W = 800 #960
SCREEN_H = 600 #720
HAR_CLAS = "haarcascade_frontalface_alt.xml"
IMG_SIZE = 150 # looking for 154
# IMG_SIZE = 80 # looking for 82

face_cascade = cv2.CascadeClassifier(HAR_CLAS)
cam = cv2.VideoCapture(0)
cam.set(3, SCREEN_W) # Width
cam.set(4, SCREEN_H) # Height

facenum = 0
working = 0
        
while(True):
    ret, img = cam.read()

    if(ret == False):
        print("Error : exiting...")
        break

    if(working > 0):
        cv2.imshow("Main Door", img)
        if(cv2.waitKey(250) & 0xFF == ord('q')):
            working = 0
            print("Face tracking resumed")
            continue
        working = working - 1
        if(working % 40 == 0):
            if(working == 0):
                print("Face tracking resumed")
            else:
                print("Face tracking is paused ...(for "+str(int(working / 4))+" seconds more)")
        continue
    
    #- Get Faces in the crowd, if any
    imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(imggray, 1.06, 4)
    if(len(faces)!=0):
        print("Psst! "+str(len(faces))+" peep(s) at the door!")
        basefile = time.strftime("%Y%m%d_%H%M%S-")
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
                cv2.imwrite('/home/pi/apps/clicks/'+str(basefile)+str(facenum)+'.jpg', imgsave)
                cv2.rectangle(img,(left,top),(left+width,top+height),(0,255,0), 4)
                facenum = facenum+1
    
        if(len(faces) == facenum):
            imgfsave = cv2.filter2D(img, -1, np.array([[0,0,0], [0,1,0], [0,0,0]]))
            cv2.imwrite('/home/pi/apps/clicks/'+str(basefile)+'f.jpg', imgfsave)
            print("Got "+str(facenum)+" faces. Uploading for identification...")
            os.system("omxplayer -o local /home/pi/apps/Christmas-doorbell-melody.mp3")
            #- Uploading to AWS for Rekognition
            file = []
            for f in range(0, facenum):
                file.append(str(basefile)+str(f)+".jpg")
                os.system('aws s3 cp /home/pi/apps/clicks/'+file[f]+' s3://standbye --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers full=emailaddress=mppise@gmail.com')
            os.system('aws s3 cp /home/pi/apps/clicks/'+str(basefile)+'f.jpg s3://standbye --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers full=emailaddress=mppise@gmail.com')
            r = requests.post("https://329qnpc5cj.execute-api.us-east-1.amazonaws.com/faces", data=json.dumps({'s3file':( ",".join(file) )}), headers={'content-type': 'application/json'})
            visitors = r.text.replace('"','').split(',')
            print(visitors)
            greeting = ""
            for v in visitors:
                if(v == "Someone"):
                    continue
                else:
                    greeting = greeting+v+", "
            if(greeting == ""):
                os.system("omxplayer -o local /home/pi/apps/clicks/greeting_standard.mp3")
            else:
                greeting = "Hello "+greeting+", on my way there. Hang on!"
                os.system('aws polly synthesize-speech --output-format "mp3" --text "'+greeting+'" --voice-id "Raveena" /home/pi/apps/clicks/greeting.mp3')
                os.system("omxplayer -o local /home/pi/apps/clicks/greeting.mp3")
            os.system("rm /home/pi/apps/clicks/*.jpg")
            working = 240
            facenum = 0
        else:
            facenum = 0

    cv2.imshow("Main Door", img)
    if(cv2.waitKey(5) & 0xFF == ord('q')):
        break

cam.release()
cv2.destroyAllWindows()
