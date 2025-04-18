from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('productos/', views.vista_stock, name ='stock')
]