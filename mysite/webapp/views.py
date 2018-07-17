from django.shortcuts import render

def index(request):
    return render(request, 'webapp/home.html')

def form(request):
    return render(request, 'webapp/form.html')