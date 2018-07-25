from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm, SubmitImageForm
import base64
# from somewhere import handle_uploaded_file # Imaginary function to handle an uploaded file.

def printPOST(request):
	post = 'post: '
	for key, value in request.POST.items():
		post = post + key +':' + value + ' '
	return HttpResponse(post)

def index(request):
	form = SubmitImageForm()
	return render(request, 'webapp/home.html', {'form': form})

def handle_uploaded_file(f):
    with open('resulted.png', 'wb') as fd:
    	fd.write(f.read())

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})