import os, requests
import json
#r = requests.get("https://329qnpc5cj.execute-api.us-east-1.amazonaws.com/faces")
#ret = r.json()
#print(json.dumps(ret["Items"]))
file=["face_0.jpg,face_1.jpg"]
r = requests.post("https://329qnpc5cj.execute-api.us-east-1.amazonaws.com/faces", data=json.dumps({'s3file':( ",".join(file) )}), headers={'content-type': 'application/json'})
visitors = r.text.replace('"','').split(',')
print(visitors)
greeting = "Hello "
for v in visitors:
    if(v == "Someone"):
        continue
    else:
        greeting = greeting+v+", "
print(greeting)
greeting = greeting+"! Be right there to get you."
print('aws polly synthesize-speech --output-format "mp3" --text "'+greeting+'" --voice-id "Raveena" /home/pi/apps/clicks/greeting.mp3')
print("omxplayer -o local /home/pi/apps/clicks/greeting.mp3")
