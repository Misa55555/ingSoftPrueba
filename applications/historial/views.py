
# Create your views here.
from django.shortcuts import render

def vistas_historial(request):
    return render(request, 'historial/historialCompras.html')

