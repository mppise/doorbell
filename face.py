import numpy as np
import cv2,time,os,requests,json

# -- Configurations -- #
SCREEN_W = 960
SCREEN_H = 720
HAR_CLAS = "haarcascade_frontalface_alt.xml"
IMG_SIZE = 125 # looking for 131

face_cascade = cv2.CascadeClassifier(HAR_CLAS)
cam = cv2.VideoCapture(0)
cam.set(3, SCREEN_W) # Width
cam.set(4, SCREEN_H) # Height

facenum = 0
working = 0

#- Rotate (http://stackoverflow.com/questions/16265673/rotate-image-by-90-180-or-270-degrees)
def rot90(img, rotflag):
    if rotflag == 1: # ClockWise
        img = cv2.transpose(img)  
        img = cv2.flip(img, 1)
    elif rotflag == 2: # Counter-ClockWise
        img = cv2.transpose(img)  
        img = cv2.flip(img, 0)
    elif rotflag ==3: # 180 flip
        img = cv2.flip(img, -1)
    elif rotflag != 0:
        raise Exception("Unknown rotation flag({})".format(rotflag))
    return img
        
while(True):
    ret, img = cam.read()
    img = rot90(img, 1)
    
    if(ret == False):
        print("Error: Camera is possibly disconnected or busy")
        cam.release()
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
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0), 4)
                    facenum = facenum+1
            cv2.imshow("Main Door", img)
            cv2.waitKey(25)
        
            if(len(faces) == facenum):
                print("Got "+str(facenum)+" faces. Uploading for identification...")
                os.system("omxplayer -o local /home/pi/apps/Christmas-doorbell-melody.mp3")
                #- Uploading to AWS for Rekognition
                file = []
                for f in range(0, facenum):
                    file.append(str(basefile)+str(f)+".jpg")
                    os.system('aws s3 cp /home/pi/apps/clicks/'+file[f]+' s3://standbye --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers full=emailaddress=mppise@gmail.com')
                r = requests.post("https://329qnpc5cj.execute-api.us-east-1.amazonaws.com/faces", data=json.dumps({'s3file':( ",".join(file) )}), headers={'content-type': 'application/json'})
                visitors = r.text.replace('"','').split(',')
                print(visitors+" at the door")
                greeting = ""
                for v in visitors:
                    if(v == "Someone"):
                        continue
                    else:
                        greeting = greeting+v+", "
                if(greeting == ""):
                    os.system("omxplayer -o local /home/pi/apps/clicks/greeting_standard.mp3")
                else:
                    greeting = "Hello "+greeting+"! I will be right there to get you."
                    os.system('aws polly synthesize-speech --output-format "mp3" --text "'+greeting+'" --voice-id "Raveena" /home/pi/apps/clicks/greeting.mp3')
                    os.system("omxplayer -o local /home/pi/apps/clicks/greeting.mp3")
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
