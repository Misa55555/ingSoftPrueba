
# Create your views here.
from django.shortcuts import render

def vista_ventas(request):
    return render(request, 'ventas/ventas.html')

