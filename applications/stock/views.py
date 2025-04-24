from django.shortcuts import render
from .models import Producto  # Importamos el modelo

def vista_stock(request):
    productos = Producto.objects.all()  # Trae todos los productos de la base
    return render(request, 'stock/stock.html', {'productos': productos})
