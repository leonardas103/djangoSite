from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import urllib.request
import json
import cv2
import numpy as np
import base64
from . import runcosfire
import os

@csrf_exempt
def detect(request):
	data = {"success": False}
	if request.method == "POST":
		image = processImage(request)
		_, buffer = cv2.imencode('.png', image)
		data.update({"result": base64.b64encode(buffer).decode('utf-8'), "success": True})
		if request.POST.get('source', None) == 'form':
			return render(request, 'webapp/postprocessing.html',{'result':data['result'], 'default': 8})
	return JsonResponse(data)


def processImage(request):
		image, type 		= getData(request,'image')
		image 				= getImage(image, type)
		prototype_select    = request.POST.get('prototype_select', None)
		if prototype_select == 'object': 
			prototype, type = getData(request,'prototype')
		else:
			prototype, type = os.getcwd() +'/webapp/static/img/'+prototype_select+'.png', 'path'
		prototype 		    = getImage(prototype, type)
		prototypeCenter,_ 	= getData(request,'prototypeCenter')
		prototypeCenter 	= tuple(prototypeCenter)
		sigma,_ 			= getData(request,'sigma')
		rhoList,_ 			= getData(request,'rhoList')
		rhoList 			= range(rhoList[0],rhoList[1],rhoList[2])
		sigma0,_ 			= getData(request,'sigma0')
		alpha,_ 			= getData(request,'alpha')
		rotInvariances,_ 	= getData(request,'rotInvariances')
		rotInvariances 		= np.arange(rotInvariances)/rotInvariances*np.pi
		result = runcosfire.main(image, prototype, prototypeCenter, sigma, rhoList, sigma0,  alpha, rotInvariances)
		return result
		

def getData(request, name):
	if request.FILES.get(name, None) is not None:
		return request.FILES[name], 'file'

	data = request.POST.get(name, None)
	if data is None:
		# data = {"error": "Sent request is missing: " + name}
		# JsonResponse(data) #must return to main
		return None

	if "/" not in data:	#only urls gets returned as string
		data = json.loads(data)
	
	return data, 'data'


def getImage(image, type):
	if type is 'data':
		with urllib.request.urlopen(image) as resp:
			image = resp.read()
	elif type is 'file':
		image = image.read()
	elif type is 'path':
		return cv2.imread(image, cv2.IMREAD_GRAYSCALE)

	image = np.asarray(bytearray(image), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
	return image
