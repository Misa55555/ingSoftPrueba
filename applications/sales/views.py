from django.shortcuts import render

# Create your views here.
# applications/sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required # Para requerir login
from django.contrib import messages # Para mostrar mensajes al usuario
from django.db.models import Q # Para búsquedas complejas
from applications.stock.models import Product, Category # Modelos de la app stock
# Importa tus nuevos modelos si necesitas interactuar con ellos directamente aquí
# from .models import Sale, SaleDetail, Client

# --- Helper Functions for Cart (Funciones de Ayuda para el Carrito) ---

def get_cart(request):
    """Obtiene el carrito de la sesión o crea uno nuevo si no existe."""
    cart = request.session.get('cart', {})
    # Asegurarnos que los valores numéricos son correctos
    for item in cart.values():
        item['quantity'] = int(item.get('quantity', 0))
        item['price'] = float(item.get('price', 0.0))
    return cart

def save_cart(request, cart):
    """Guarda el carrito en la sesión."""
    request.session['cart'] = cart
    request.session.modified = True

def calculate_cart_total(cart):
    """Calcula el total del carrito."""
    total = sum(item['quantity'] * item['price'] for item in cart.values())
    return round(total, 2)

# --- Views (Vistas) ---

@login_required # Asegura que el usuario esté logueado para acceder a ventas
def pos_view(request):
    # Lógica de Búsqueda y Filtrado
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', None)
    products = Product.objects.select_related('brand', 'category').filter(stock__gt=0) # Solo productos con stock

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(bar_code__icontains=query) |
            Q(category__name__icontains=query) | # Busca también por nombre de categoría
            Q(brand__name__icontains=query)      # Busca también por nombre de marca
        )

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all() # Para los botones de filtro

    # Obtener Carrito y Total
    cart = get_cart(request)
    cart_total = calculate_cart_total(cart)
    # Preparar items del carrito para la plantilla (convertir IDs a objetos si es necesario o añadir más info)
    # Por ahora, pasamos el diccionario directamente, la plantilla puede manejarlo.
    # Si necesitas info completa del producto en la plantilla del carrito, puedes hacer:
    cart_items_detailed = []
    product_ids_in_cart = [int(pid) for pid in cart.keys()] # Obtener IDs como enteros
    products_in_cart = Product.objects.in_bulk(product_ids_in_cart) # Consulta eficiente

    for product_id_str, item_data in cart.items():
       product_id = int(product_id_str)
       product = products_in_cart.get(product_id)
       if product: # Asegurarse que el producto aún existe
           cart_items_detailed.append({
               'product_id': product_id,
               'name': product.name,
               'quantity': item_data['quantity'],
               'price': item_data['price'], # Precio guardado en el carrito (podría ser product.price si siempre quieres el actual)
               'subtotal': round(item_data['quantity'] * item_data['price'], 2)
           })
       # else: Podrías manejar el caso de un producto en carrito que ya no existe

    context = {
        'products': products.order_by('name'),
        'categories': categories,
        'cart_items': cart_items_detailed, # Usamos la lista detallada
        'cart_total': cart_total,
        'search_query': query,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'sales/pos_interface.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, stock__gt=0) # Asegura que existe y hay stock
    cart = get_cart(request)
    product_id_str = str(product_id) # Las claves de sesión suelen ser strings

    if product_id_str in cart:
        # Incrementar cantidad si ya está en el carrito
        # Validar stock antes de incrementar
        if product.stock > cart[product_id_str]['quantity']:
             cart[product_id_str]['quantity'] += 1
             messages.success(request, f"'{product.name}' cantidad actualizada en el carrito.")
        else:
            messages.warning(request, f"No hay suficiente stock para añadir más '{product.name}'.")

    else:
        # Añadir nuevo producto al carrito
        cart[product_id_str] = {
            'quantity': 1,
            'price': float(product.price), # Guardar precio actual como float
            'name': product.name # Guardar nombre para fácil acceso (opcional)
        }
        messages.success(request, f"'{product.name}' añadido al carrito.")

    save_cart(request, cart)
    # Redirigir de vuelta a la vista POS
    # Es mejor usar reverse para evitar hardcodear URLs
    return redirect(reverse('sales:pos_view') + f'?q={request.GET.get("q","")}&category={request.GET.get("category","")}')

@login_required
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)

    if product_id_str in cart:
        product_name = cart[product_id_str].get('name', f'Producto ID {product_id_str}')
        del cart[product_id_str]
        save_cart(request, cart)
        messages.info(request, f"'{product_name}' eliminado del carrito.")
    else:
         messages.warning(request, "El producto no se encontró en el carrito.")

    return redirect(reverse('sales:pos_view') + f'?q={request.GET.get("q","")}&category={request.GET.get("category","")}')


@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 1:
                # Si la cantidad es 0 o menos, eliminar el item
                return remove_from_cart(request, product_id)

            cart = get_cart(request)
            product_id_str = str(product_id)

            if product_id_str in cart:
                product = get_object_or_404(Product, id=product_id) # Necesitamos verificar stock
                if product.stock >= quantity:
                    cart[product_id_str]['quantity'] = quantity
                    save_cart(request, cart)
                    messages.success(request, f"Cantidad de '{product.name}' actualizada.")
                else:
                    messages.error(request, f"Stock insuficiente para '{product.name}'. Disponible: {product.stock}")
            else:
                 messages.warning(request, "El producto no se encontró en el carrito.")

        except (ValueError, TypeError):
            messages.error(request, "Cantidad inválida.")

    # Siempre redirige a la vista POS, preservando filtros/búsqueda si es posible
    # Construye la URL de redirección con los parámetros GET actuales
    redirect_url = reverse('sales:pos_view')
    query_params = request.GET.urlencode() # Obtiene q=...&category=...
    if query_params:
        redirect_url += '?' + query_params
    return redirect(redirect_url)


@login_required
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
        messages.info(request, "Carrito vaciado.")
    return redirect(reverse('sales:pos_view') + f'?q={request.GET.get("q","")}&category={request.GET.get("category","")}')


@login_required
def checkout_view(request):
    # --- ESTA ES LA PARTE QUE SE COMPLETARÁ EN LA FASE 2 ---
    # Por ahora, solo muestra un mensaje o redirige.
    # Aquí iría la lógica para:
    # 1. Validar el carrito (que no esté vacío).
    # 2. (Opcional) Seleccionar/Crear Cliente.
    # 3. Verificar stock de todos los productos OTRA VEZ (importante!).
    # 4. Iniciar una transacción de base de datos.
    # 5. Crear el objeto Sale.
    # 6. Crear los objetos SaleDetail.
    # 7. Decrementar el stock de los Product.
    # 8. Commit de la transacción.
    # 9. Limpiar el carrito de la sesión.
    # 10. Mostrar página de éxito o redirigir.

    cart = get_cart(request)
    if not cart:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('sales:pos_view')

    # Simulación temporal: Limpiar carrito y mostrar mensaje
    messages.success(request, "¡Procediendo al pago! (Funcionalidad pendiente)")
    # En un futuro, aquí NO limpiarías el carrito hasta que el pago se confirme
    # clear_cart(request) # No limpiar aquí todavía

    # Puedes redirigir a una página de 'confirmación de pago' pendiente
    # O simplemente volver al POS por ahora
    return redirect('sales:pos_view')