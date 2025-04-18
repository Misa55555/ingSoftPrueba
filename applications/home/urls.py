from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('inicio/', views.vista_home, name ='home')
]