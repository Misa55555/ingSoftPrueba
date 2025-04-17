from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('prueba/', views.PruebaView.as_view(), name='prueba')
]
