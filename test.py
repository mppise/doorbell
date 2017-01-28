import os, requests
import json
r = requests.get("https://329qnpc5cj.execute-api.us-east-1.amazonaws.com/faces")
ret = r.json()
print(json.dumps(ret["Items"]))
