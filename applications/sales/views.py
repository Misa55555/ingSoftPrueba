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
from .forms import ClientForm # Importar el nuevo formulario
from django.urls import reverse_lazy # Para redirección

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
    """Calcula el total del carrito usando Decimal."""
    total = Decimal('0.00') # Inicializar como Decimal
    for item in cart.values():
        try:
            # Convertir cantidad (int) y precio (str) a Decimal para multiplicar
            quantity = Decimal(item.get('quantity', 0))
            price = Decimal(item.get('price', '0.00'))
            total += quantity * price
        except (InvalidOperation, TypeError, KeyError):
             # Manejar posible error si los datos del carrito son inválidos
             # Puedes loggear un error aquí si quieres
             print(f"Advertencia: Item inválido en el carrito: {item}")
             continue # Saltar este item

    # No necesitas round() si operas solo con Decimal y tus precios tienen 2 decimales
    # .quantize asegura que el resultado tenga exactamente 2 decimales
    return total.quantize(Decimal('0.01'))

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
            'price': str(product.price), # Guardar precio actual como float
            'name': product.name # Guardar nombre para fácil acceso (opcional)
        }
        messages.success(request, f"'{product.name}' añadido al carrito.")

    save_cart(request, cart)
    # Preservar filtros/búsqueda en redirección
    redirect_url = reverse('sales:pos_view')
    query_params = request.GET.urlencode()
    if query_params:
        redirect_url += '?' + query_params
    return redirect(redirect_url)

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

    # --- CALCULO INICIAL ---
    # cart_subtotal SIEMPRE representa el total ANTES de descuentos
    cart_subtotal = calculate_cart_total(cart)
    clients = Client.objects.all().order_by('client_name')
    payment_choices = Sale.PAYMENT_METHOD_CHOICES
    new_client_id_from_url = request.GET.get('new_client_id')

    if request.method == 'POST':
        # --- OBTENER DATOS DEL POST ---
        client_id = request.POST.get('client_id')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '')
        amount_received_str = request.POST.get('amount_received')
        discount_amount_str = request.POST.get('discount_amount', '0')
        discount_reason = request.POST.get('discount_reason', '')

        # --- INICIALIZAR VARIABLES ---
        selected_client = None
        amount_received = None # Será Decimal si es efectivo y válido
        change_given = None    # Será Decimal si es efectivo y hay cambio
        discount_amount = Decimal('0.00') # Será Decimal validado
        final_total = cart_subtotal # Total a pagar empieza como subtotal

        # --- BLOQUE try...except PARA VALIDACIONES PREVIAS ---
        # Usamos un try/except general para las validaciones que redirigen
        # al formulario con errores.
        try:
            # --- Validación de Cliente ---
            if client_id:
                try:
                    selected_client = Client.objects.get(id=client_id)
                except Client.DoesNotExist:
                    messages.error(request, "Cliente seleccionado inválido.")
                    raise ValidationError("Cliente inválido") # Para ir al render error

            # --- Validación de Método de Pago ---
            if not payment_method or payment_method not in [code for code, name in Sale.PAYMENT_METHOD_CHOICES]:
                 messages.error(request, "Método de pago inválido.")
                 raise ValidationError("Pago inválido")

            # --- Validación y Cálculo de Descuento ---
            try:
                discount_amount = Decimal(discount_amount_str) if discount_amount_str else Decimal('0.00')
                if discount_amount < 0:
                    messages.error(request, "El descuento no puede ser negativo.")
                    raise ValidationError("Descuento negativo")
                if discount_amount > cart_subtotal:
                     messages.error(request, "El descuento no puede ser mayor que el subtotal.")
                     raise ValidationError("Descuento excede subtotal")
            except InvalidOperation:
                messages.error(request, "Monto de descuento inválido.")
                raise ValidationError("Descuento inválido")

            # --- Calcular Total Final ---
            final_total = cart_subtotal - discount_amount # Total a pagar DESPUÉS de descuento

            # --- Validación de Efectivo (si aplica) ---
            if payment_method == 'cash':
                if not amount_received_str:
                    messages.error(request, "Debe ingresar el monto recibido para pago en efectivo.")
                    raise ValidationError("Falta monto recibido")
                try:
                    amount_received = Decimal(amount_received_str)
                    # >>> CORRECCIÓN IMPORTANTE: Comparar con final_total <<<
                    if amount_received < final_total:
                        messages.error(request, "El efectivo recibido debe ser mayor o igual al total a pagar (después del descuento).")
                        raise ValidationError("Efectivo insuficiente")
                    # >>> CORRECCIÓN IMPORTANTE: Calcular cambio aquí <<<
                    change_given = amount_received - final_total
                except InvalidOperation:
                    messages.error(request, "Monto recibido inválido.")
                    raise ValidationError("Monto recibido inválido")

        # --- FIN BLOQUE try...except PARA VALIDACIONES ---
        except ValidationError:
             # Si alguna validación falló, renderizar de nuevo el formulario
             return render(request, 'sales/checkout.html', {
                 'cart': cart, 'cart_items': get_detailed_cart_items(cart),
                 'cart_total': cart_subtotal, # Pasar subtotal
                 'clients': clients, 'payment_choices': payment_choices,
                 'selected_client_id': client_id, # Mantener selección
                 'selected_payment_method': payment_method,
                 'notes': notes, 'amount_received': amount_received_str, # Devolver strings originales
                 'discount_amount': discount_amount_str,
                 'discount_reason': discount_reason,
             })

        # --- Si TODAS las validaciones previas pasaron, proceder con la transacción ---
        try:
            with transaction.atomic():
                # 1. Validar stock y bloquear (igual que antes)
                products_to_update = []
                for product_id_str, item_data in cart.items():
                     product_id = int(product_id_str)
                     quantity_to_sell = item_data['quantity']
                     # Usar try-except por si el producto fue borrado mientras estaba en carrito
                     try:
                         product = Product.objects.select_for_update().get(id=product_id)
                     except Product.DoesNotExist:
                          raise ValueError(f"Producto ID {product_id} no encontrado. Elimínelo del carrito.")

                     if product.stock < quantity_to_sell:
                         raise ValueError(f"Stock insuficiente para '{product.name}'. Disponible: {product.stock}, Solicitado: {quantity_to_sell}")
                     products_to_update.append({'product': product, 'quantity': quantity_to_sell, 'price': Decimal(item_data.get('price', '0.00'))}) # Guardar precio Decimal aquí también

                # 2. Crear la Venta (Sale) con todos los datos validados y calculados
                sale = Sale.objects.create(
                    client=selected_client,
                    seller=request.user,
                    total_amount=final_total,        # <-- Total FINAL
                    payment_method=payment_method,
                    amount_received=amount_received, # <-- Monto recibido (Decimal o None)
                    change_given=change_given,       # <-- Cambio calculado (Decimal o None)
                    discount_amount=discount_amount, # <-- Descuento (Decimal)
                    discount_reason=discount_reason,
                    notes=notes
                )

                # 3. Crear Detalles y Actualizar Stock
                for item in products_to_update:
                    product = item['product']
                    quantity = item['quantity']
                    unit_price = item['price'] # Usar el precio Decimal guardado
                    SaleDetail.objects.create(
                        sale=sale, product=product, quantity=quantity, unit_price=unit_price
                    )
                    # Decrementar stock
                    product.stock = F('stock') - quantity
                    product.save(update_fields=['stock'])

            # --- FIN Transacción Atómica ---

            # 4. Limpiar carrito si todo OK
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

            # 5. Redirigir a Recibo
            messages.success(request, f"¡Venta #{sale.id} registrada exitosamente!")
            return redirect(reverse('sales:sale_receipt', args=[sale.id]))

        # --- Manejo de Errores de la Transacción (ej. Stock) ---
        except ValueError as e: # Error de stock u otro ValueError
            messages.error(request, str(e))
        except Exception as e: # Otros errores inesperados
            messages.error(request, f"Ocurrió un error inesperado al procesar la venta: {e}")

        # Volver a renderizar si hubo error DENTRO de la transacción
        return render(request, 'sales/checkout.html', {
              'cart': cart, 'cart_items': get_detailed_cart_items(cart),
              'cart_total': cart_subtotal, 'clients': clients, 'payment_choices': payment_choices,
              'selected_client_id': client_id, 'selected_payment_method': payment_method,
              'notes': notes, 'amount_received': amount_received_str,
              'discount_amount': discount_amount_str, 'discount_reason': discount_reason,
         })

    else: # Método GET
        # --- Lógica GET (sin cambios significativos) ---
        cart_items_detailed = get_detailed_cart_items(cart)
        selected_client_id_on_load = new_client_id_from_url or ''
        context = {
            'cart': cart,
            'cart_items': cart_items_detailed,
            'cart_total': cart_subtotal, # Pasar subtotal para display inicial
            'clients': clients,
            'payment_choices': payment_choices,
            'selected_client_id': selected_client_id_on_load,
        }
        return render(request, 'sales/checkout.html', context)


@login_required
def sale_receipt_view(request, sale_id):
    """
    Muestra los detalles de una venta específica en formato de recibo.
    """
    try:
        # Optimizamos la consulta para obtener datos relacionados eficientemente
        sale = Sale.objects.select_related('client', 'seller').prefetch_related(
            'details', # Prefetch detalles
            'details__product', # Prefetch producto dentro de detalles
            'details__product__brand', # Prefetch marca dentro de producto (opcional)
            'details__product__category' # Prefetch categoría dentro de producto (opcional)
        ).get(id=sale_id)

        # Podrías añadir una verificación extra, por ejemplo,
        # si solo el vendedor que hizo la venta o un admin puede verla.
        # if not request.user.is_staff and sale.seller != request.user:
        #     messages.error(request, "No tienes permiso para ver este recibo.")
        #     return redirect('sales:pos_view') # O a donde corresponda

    except Sale.DoesNotExist:
        messages.error(request, "La venta solicitada no existe.")
        return redirect('sales:pos_view') # O a una página de historial de ventas

    context = {
        'sale': sale,
        # Podrías pasar datos de la 'empresa' aquí desde settings más adelante
        'company_name': "Mi Negocio XYZ (Placeholder)",
        'company_address': "Calle Falsa 123, Ciudad (Placeholder)",
        'company_phone': "+54 9 351 1234567 (Placeholder)",
    }
    return render(request, 'sales/receipt.html', context)

@login_required
def add_client_view(request):
    """
    Maneja la creación de un nuevo cliente.
    Redirige de vuelta al checkout pre-seleccionando el cliente creado.
    """
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                new_client = form.save()
                messages.success(request, f"Cliente '{new_client.client_name}' añadido exitosamente.")
                # Redirigir de vuelta al checkout, pasando el ID del nuevo cliente
                checkout_url = reverse('sales:checkout')
                return redirect(f'{checkout_url}?new_client_id={new_client.id}')
            except Exception as e:
                # Capturar errores inesperados al guardar (ej. CUIT duplicado no manejado por form)
                messages.error(request, f"Error al guardar el cliente: {e}")
                # Se vuelve a mostrar el formulario con los errores implícitos del form
    else: # Método GET
        form = ClientForm()

    context = {
        'form': form,
        'title': 'Añadir Nuevo Cliente'
    }
    # Reutilizamos una plantilla genérica de formulario o creamos una específica
    return render(request, 'sales/generic_form.html', context)

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