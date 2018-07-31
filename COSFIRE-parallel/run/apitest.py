import requests
import cv2
import base64
import numpy as np
 
url = "http://localhost:8000/api/"

files, data 			= {}, {}
files['image'] 			= open("fox.jpg", "rb")
files['prototype'] 		= open("line.png", "rb")
data['prototypeCenter'] = '[100,100]'
data['sigma'] 			= '2.4'
data['rhoList'] 		= '[0,9,2]'
data['sigma0'] 			= '3'
data['alpha']		 	= '0.7'
data['rotInvariances'] 	= '12'
r = requests.post(url, files=files, data=data).json()
image = r["result"]

#Save the image
image = base64.b64decode(image)
with open('result.png', 'wb') as fd:
    fd.write(image)

#postprocessing
im_tresh = cv2.imdecode(np.asarray(bytearray(image), dtype="uint8"), cv2.IMREAD_GRAYSCALE)
im_tresh = cv2.threshold(im_tresh, cv2.THRESH_OTSU, 255, cv2.THRESH_BINARY)[1]
cv2.imshow('image',im_tresh)
cv2.waitKey(0)