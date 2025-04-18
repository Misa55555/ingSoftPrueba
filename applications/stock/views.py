
# Create your views here.
from django.shortcuts import render

def vista_stock(request):
    return render(request, 'stock/stock.html')

