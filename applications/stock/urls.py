# applications/stock/urls.py
from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Vista principal de gestión de stock (reemplaza la anterior si la tenías)
    path('', views.manage_stock_view, name='manage_stock'), # Era product_list_create

    # --- URLs para las Vistas AJAX de los Modales ---
    path('ajax/add-category/', views.add_category_ajax, name='add_category_ajax'),
    path('ajax/add-brand/', views.add_brand_ajax, name='add_brand_ajax'),
    path('ajax/add-supplier/', views.add_supplier_ajax, name='add_supplier_ajax'),

    # Podrías tener otras URLs aquí, como detalle de producto, editar producto, etc.
    # path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    # path('product/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
]