from django.shortcuts import render

# Create your views here.

# applications/stock/views.py

from django.shortcuts import render, redirect
from .models import Product, Brand, Category # Asegúrate de importar Brand y Category si las necesitas directamente en la vista, aunque el formulario las maneja.
from .forms import ProductForm

def product_list_and_create(request):
    # Procesar el formulario si la petición es POST
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo producto en la BBDD
            # Redirige a la misma página (usando el nombre de la URL)
            # Esto sigue el patrón Post/Redirect/Get para evitar reenvíos del formulario
            return redirect('stock:product_list_create')
        # Si el formulario NO es válido, se renderizará de nuevo abajo
        # con los errores.
    else:
        # Si la petición es GET, crea un formulario vacío
        form = ProductForm()

    # Obtener todos los productos para mostrarlos en la lista
    # Ordenamos por ID descendente para ver los últimos agregados primero
    products = Product.objects.select_related('brand', 'category').order_by('-id')

    # Prepara el contexto para la plantilla
    context = {
        'form': form,
        'products': products,
    }
    # Renderiza la plantilla con el contexto
    return render(request, 'stock/product_form_list.html', context)