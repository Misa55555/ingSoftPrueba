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
from django.db import transaction
from django.db.models import F # Para actualizar stock de forma segura
from .models import Client, Sale, SaleDetail
# --- Helper Functions for Cart (Funciones de Ayuda para el Carrito) ---
from decimal import Decimal, InvalidOperation # Importar Decimal e InvalidOperation

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
    cart = get_cart(request)
    if not cart:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('sales:pos_view')

    cart_total = calculate_cart_total(cart)
    clients = Client.objects.all()
    payment_choices = Sale.PAYMENT_METHOD_CHOICES # Pasar choices a la plantilla

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '') # Obtener notas
        amount_received_str = request.POST.get('amount_received')

        selected_client = None
        amount_received = None
        change_given = None

        # --- Validación de Datos del Formulario (Antes de la transacción) ---
        if client_id:
            try:
                selected_client = Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                messages.error(request, "Cliente seleccionado inválido.")
                # Volver a renderizar con error y datos previos
                return render(request, 'sales/checkout.html', {
                    'cart': cart,
                    'cart_items': get_detailed_cart_items(cart),
                    'cart_total': cart_total,
                    'clients': clients,
                    'payment_choices': payment_choices, # Reenviar choices
                    'selected_client_id': client_id, # Mantener selección
                    'selected_payment_method': payment_method, # Mantener selección
                    'notes': notes, # Mantener notas
                    'amount_received': amount_received_str, # Mantener monto
                })

        if not payment_method or payment_method not in [code for code, name in Sale.PAYMENT_METHOD_CHOICES]:
             messages.error(request, "Método de pago inválido.")
             # Volver a renderizar con error (similar a arriba)
             # ... (código de renderizado de error omitido por brevedad) ...
             return render(request, 'sales/checkout.html', { # ... contexto ...
                 'selected_payment_method': payment_method, # Pasar el inválido para depuración si quieres
              })


        if payment_method == 'cash':
            if not amount_received_str:
                messages.error(request, "Debe ingresar el monto recibido para pago en efectivo.")
                # Volver a renderizar con error
                # ... (código de renderizado de error omitido) ...
                return render(request, 'sales/checkout.html', { # ... contexto ...
                     'selected_payment_method': payment_method,
                })
            try:
                amount_received = Decimal(amount_received_str)
                if amount_received < cart_total:
                    messages.error(request, "El efectivo recibido debe ser mayor o igual al total.")
                    # Volver a renderizar con error
                    # ... (código de renderizado de error omitido) ...
                    return render(request, 'sales/checkout.html', { # ... contexto ...
                          'selected_payment_method': payment_method,
                          'amount_received': amount_received_str,
                    })
                change_given = amount_received - cart_total
            except InvalidOperation:
                messages.error(request, "Monto recibido inválido.")
                # Volver a renderizar con error
                # ... (código de renderizado de error omitido) ...
                return render(request, 'sales/checkout.html', { # ... contexto ...
                      'selected_payment_method': payment_method,
                       'amount_received': amount_received_str,
                 })
        # --- Validación extra: Recalcular total desde base de datos ---
            

        # --- Si las validaciones pasan, proceder con la transacción ---
        try:
            with transaction.atomic():
                # 1. Validar stock y bloquear (sin cambios aquí)
                products_to_update = []
                for product_id_str, item_data in cart.items():
                    # ... (lógica de select_for_update y chequeo de stock igual que antes) ...
                     product_id = int(product_id_str)
                     quantity_to_sell = item_data['quantity']
                     product = Product.objects.select_for_update().get(id=product_id)
                     if product.stock < quantity_to_sell:
                         raise ValueError(f"Stock insuficiente para '{product.name}'. Disponible: {product.stock}, Solicitado: {quantity_to_sell}")
                     products_to_update.append({'product': product, 'quantity': quantity_to_sell})


                # 2. Crear la Venta (Sale) con los nuevos campos
                sale = Sale.objects.create(
                    client=selected_client,
                    seller=request.user,
                    total_amount=cart_total,
                    payment_method=payment_method, # Guardar método
                    amount_received=amount_received, # Guardar monto recibido (será None si no es cash)
                    change_given=change_given,       # Guardar cambio (será None si no es cash)
                    notes=notes                     # Guardar notas
                )

                # 3. Crear Detalles y Actualizar Stock (sin cambios aquí)
                for item in products_to_update:
                    # ... (lógica de crear SaleDetail y decrementar stock con F() igual que antes) ...
                    product = item['product']
                    quantity = item['quantity']
                    unit_price = cart[str(product.id)]['price']
                    SaleDetail.objects.create(
                        sale=sale, product=product, quantity=quantity, unit_price=unit_price
                    )
                    product.stock = F('stock') - quantity
                    product.save(update_fields=['stock'])

            # 4. Limpiar carrito (sin cambios)
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

            # 5. Redirigir (sin cambios)
            messages.success(request, f"¡Venta #{sale.id} registrada exitosamente!")
            return redirect('sales:pos_view')

        except ValueError as e: # Error de stock
            messages.error(request, str(e))
        except Exception as e: # Otros errores
            messages.error(request, f"Ocurrió un error inesperado al procesar la venta: {e}")

        # Volver a renderizar si hubo error en la transacción
        return render(request, 'sales/checkout.html', {
             'cart': cart,
             'cart_items': get_detailed_cart_items(cart),
             'cart_total': cart_total,
             'clients': clients,
             'payment_choices': payment_choices,
             'selected_client_id': client_id,
             'selected_payment_method': payment_method,
             'notes': notes,
             'amount_received': amount_received_str,
        })

    else: # Método GET
        cart_items_detailed = get_detailed_cart_items(cart)
        context = {
            'cart': cart,
            'cart_items': cart_items_detailed,
            'cart_total': cart_total,
            'clients': clients,
            'payment_choices': payment_choices, # Pasar choices a la plantilla
        }
        return render(request, 'sales/checkout.html', context)


# --- Helper Adicional (similar al de pos_view) ---
# (Puedes mover esto y los otros helpers a un archivo 'utils.py' e importarlos)
def get_detailed_cart_items(cart):
    """Obtiene detalles de los productos en el carrito para mostrar en plantilla."""
    cart_items_detailed = []
    product_ids_in_cart = [int(pid) for pid in cart.keys()]
    products_in_cart = Product.objects.in_bulk(product_ids_in_cart) # Consulta eficiente

    for product_id_str, item_data in cart.items():
       product_id = int(product_id_str)
       product = products_in_cart.get(product_id)
       if product:
           cart_items_detailed.append({
               'product_id': product_id,
               'name': product.name,
               'quantity': item_data['quantity'],
               'price': item_data['price'],
               'subtotal': round(item_data['quantity'] * item_data['price'], 2)
           })
    return cart_items_detailed