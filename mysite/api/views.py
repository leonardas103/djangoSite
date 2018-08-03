from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import urllib.request
import json
import cv2
import numpy as np
import base64
from . import runcosfire

@csrf_exempt
def detect(request):
	data = {"success": False}
	if request.method == "POST":
		image = processImage(request)
		_, buffer = cv2.imencode('.png', image)
		data.update({"result": base64.b64encode(buffer).decode('utf-8'), "success": True})
		if request.POST.get('source', None) == 'form':
			imagehtml =  '<img src="data:image/png;base64,' + data['result'] + '"/>'
			return render(request, 'webapp/postprocessing.html')
			# return HttpResponse(imagehtml)
	return JsonResponse(data)

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
		rotInvariances,_ 	= getData(request,'rotInvariances')
		rotInvariances 		= np.arange(rotInvariances)/rotInvariances*np.pi
		result = runcosfire.main(image, prototype, prototypeCenter, sigma, rhoList, sigma0,  alpha, rotInvariances)
		return result
		

def getData(request, name):
	if request.FILES.get(name, None) is not None:
		return request.FILES[name], 'file'

	data = request.POST.get(name, None)
	if data is None:
		data = {"error": "Sent request is missing: " + name}
		return JsonResponse(data) #must return to main
	
	if "/" not in data:	#only urls gets returned as string
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
