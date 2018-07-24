import requests
import cv2
import base64
import io
import numpy as np
from PIL import Image
 
url = "http://localhost:8000/api/"

# payload = {"image": "https://www.pyimagesearch.com/wp-content/uploads/2015/05/obama.jpg"}
# r = requests.post(url, data=payload).json()
 
# image = cv2.imread("eye2.png")
files, data 			= {}, {}
# files['image'] 			= open("01_test.tif", "rb")
data['image'] 			= "https://movetonetherlands.com/wp-content/uploads/NL-UK-USA-AUS-traffic-sign-comparison.jpg"
files['prototype'] 		= open("line.png", "rb")
data['prototypeCenter'] ='[100,100]'
data['sigma'] 			= '2.4'
data['rhoList'] 		= '[0,9,2]'
data['sigma0'] 			= '3'
data['alpha']		 	= '0.7'
data['rotInvariance'] 	= '12'
r = requests.post(url, files=files, data=data).json()


image = r["image"]
image = base64.b64decode(image)
with open('result.png', 'wb') as fd:
    fd.write(image)

r["image"] = None
print ("http response: {}".format(r))

#postprocessing
im_tresh = cv2.imdecode(np.asarray(bytearray(image), dtype="uint8"), cv2.IMREAD_GRAYSCALE)
im_tresh = cv2.threshold(im_tresh, cv2.THRESH_OTSU*5, 255, cv2.THRESH_BINARY)[1]
cv2.imshow('image',im_tresh)
cv2.waitKey(0)