from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import SubmitImageForm

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