# applications/sales/urls.py

from django.urls import path
from . import views

app_name = 'sales' # Namespace

urlpatterns = [
    path('', views.pos_view, name='pos_view'),
    # Añadiremos más URLs para acciones específicas del carrito y checkout después
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'), # Para actualizar cantidad
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout_view, name='checkout'), # Placeholder para el botón "Pagar"
]