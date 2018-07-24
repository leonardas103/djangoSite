from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import numpy as np
import urllib.request
import json
import cv2
import os
import base64
from . import runcosfire


@csrf_exempt
def detect(request):
	data = {"success": False}
	if request.method == "POST":
		image = processImage(request)
		# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		_, buffer = cv2.imencode('.png', image)
		# base64u.rlsafe_b64encode
		data.update({"image": base64.b64encode(buffer).decode('utf-8'), "success": True})
	return JsonResponse(data)	# return a JSON response

def processImage(request):
		image, type 		= getData(request,'image')
		image 				= getImage(image, type)
		prototype, type 	= getData(request,'prototype')
		prototype 			= getImage(prototype, type)
		prototypeCenter,_ 	= getData(request,'prototypeCenter')
		prototypeCenter 	= tuple(prototypeCenter)
		sigma,_ 			= getData(request,'sigma')
		rhoList,_ 			= getData(request,'rhoList')
		rhoList 			= range(rhoList[0],rhoList[1],rhoList[2])
		sigma0,_ 			= getData(request,'sigma0')
		alpha,_ 			= getData(request,'alpha')
		rotInvariance,_ 	= getData(request,'rotInvariance')
		rotInvariance 		= np.arange(rotInvariance)/rotInvariance*np.pi
		result = runcosfire.main(image, prototype, prototypeCenter, sigma, rhoList, sigma0,  alpha, rotInvariance)
		return result
		

def getData(request, name):
	if request.FILES.get(name, None) is not None:
		return request.FILES[name], 'file'

	data = request.POST.get(name, None)
	if data is None:
		data["error"] = "Sent request is missing: " + name
		return JsonResponse(data)
	
	if "/" not in data:
		data = json.loads(data)
	
	return data, 'data'

def getImage(image, type):
	if type is 'data':
		with urllib.request.urlopen(image) as resp:
			data = resp.read()
	elif type is 'file':
		data = image.read()

	image = np.asarray(bytearray(data), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
	return image
