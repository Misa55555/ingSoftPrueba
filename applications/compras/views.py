
# Create your views here.
from django.shortcuts import render

def vistas_compras(request):
    return render(request, 'compras/compras.html')

