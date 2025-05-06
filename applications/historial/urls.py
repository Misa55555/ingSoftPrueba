from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.vistas_historial, name ='historial_compras')
]