from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('about/', views.about, name='about'),
    path('postprocessing/', views.postprocessing, name='postprocessing'),
]