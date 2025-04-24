
# Create your views here.
from django.shortcuts import render, redirect
from .forms import ProductoForm  # Importamos el formulario que hicimos

def vistas_compras(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el producto en la base de datos
            return redirect('stock')  # Cambialo si tu vista de stock tiene otro nombre
    else:
        form = ProductoForm()
    
    return render(request, 'compras/compras.html', {'form': form})
