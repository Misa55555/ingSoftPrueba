from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('vender/', views.vista_ventas, name ='ventas')
]