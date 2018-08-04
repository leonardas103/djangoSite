from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import SubmitImageForm
import numpy as np
import base64
import cv2

def printPOST(request):
	post = 'post: '
	for key, value in request.POST.items():
		post = post + key +':' + value + ' '
	return HttpResponse(post)

def index(request):
	form = SubmitImageForm()
	return render(request, 'webapp/home.html', {'form': form})

def info(request):
	return render(request, 'webapp/info.html')

def about(request):
	return render(request, 'webapp/about.html')

def postprocessing(request):
	if request.method == "POST":
		threshold = int(request.POST.get('threshold', None))
		image = request.POST.get('result', None)
		result = thresholdImage(image, threshold)
		if image == result:
			resp_body = '<script>alert("The image is already thresholded. You will be taken back.");window.history.go(-2);</script>'
			return HttpResponse(resp_body)
		return render(request, 'webapp/postprocessing.html',{'result':result, 'default':threshold})
	return render(request, 'webapp/postprocessing.html')

def thresholdImage(image, threshold):
	result = base64.b64decode(str(image))
	result = cv2.imdecode(np.asarray(bytearray(result), dtype="uint8"), cv2.IMREAD_GRAYSCALE)
	result = cv2.threshold(result, threshold, 255, cv2.THRESH_BINARY)[1]
	_, buffer = cv2.imencode('.png', result)
	return base64.b64encode(buffer).decode('utf-8')