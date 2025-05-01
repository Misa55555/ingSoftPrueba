# applications/stock/urls.py

from django.urls import path
from . import views

# Define un namespace para evitar colisiones de nombres de URL con otras apps
app_name = 'stock'

urlpatterns = [
    # La URL raíz dentro de la app ('/stock/') mostrará el formulario y la lista
    path('', views.product_list_and_create, name='product_list_create'),
]