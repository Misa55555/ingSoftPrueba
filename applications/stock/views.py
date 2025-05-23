# applications/stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse # Para respuestas AJAX
from django.template.loader import render_to_string # Para renderizar partes de plantillas a string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction # Para la carga de remitos
from django.db.models import F # Para actualizar stock

from .models import Product, Category, Brand, Supplier, StockEntry, StockEntryDetail
from .forms import (
    ProductForm, CategoryFormModal, BrandFormModal, SupplierFormModal,
    StockEntryForm, StockEntryDetailFormSet
)
# Asumo que tienes tus decoradores de roles si los vas a usar aquí.
# from applications.dashboard.decorators import admin_required, group_required


# --- VISTAS AJAX PARA MODALES ---

@login_required
# @admin_required # O el permiso que corresponda para crear estas entidades
def add_category_ajax(request):
    if request.method == 'POST':
        form = CategoryFormModal(request.POST)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Categoría creada exitosamente.',
                'new_option_value': category.id,
                'new_option_text': category.name
            })
        else:
            # Renderizar el formulario con errores para mostrar en el modal
            form_html = render_to_string('stock/partials/modal_form_content.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
# @admin_required
def add_brand_ajax(request):
    if request.method == 'POST':
        form = BrandFormModal(request.POST)
        if form.is_valid():
            brand = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Marca creada exitosamente.',
                'new_option_value': brand.id,
                'new_option_text': brand.name
            })
        else:
            form_html = render_to_string('stock/partials/modal_form_content.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
# @admin_required
def add_supplier_ajax(request):
    if request.method == 'POST':
        form = SupplierFormModal(request.POST)
        if form.is_valid():
            supplier = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Proveedor creado exitosamente.',
                'new_option_value': supplier.id,
                'new_option_text': supplier.name
            })
        else:
            form_html = render_to_string('stock/partials/modal_form_content.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# applications/stock/views.py
# ... (importaciones existentes y vistas AJAX arriba) ...

@login_required
def manage_stock_view(request):
    # --- PERMISOS (Ejemplo) ---
    # Solo administradores pueden cargar productos o remitos
    can_manage_fully = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()
    # Empleados podrían solo ver la lista (ajusta según tus roles)
    # if not (can_manage_fully or request.user.groups.filter(name='Empleado').exists()):
    #     messages.error(request, "No tienes permiso para acceder a esta sección.")
    #     return redirect('home') # O a donde corresponda

    # --- Instanciar Formularios ---
    product_form = ProductForm(prefix='product') # Prefijo para distinguir campos si hay colisiones
    stock_entry_form = StockEntryForm(prefix='entry')
    stock_entry_detail_formset = StockEntryDetailFormSet(prefix='details')

    # --- Manejo de POST ---
    if request.method == 'POST':
        if not can_manage_fully: # Doble chequeo de permiso para POST
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect(reverse('stock:manage_stock'))

        # Determinar qué formulario se envió usando el nombre del botón de submit
        if 'submit_product' in request.POST: # Botón del formulario de producto
            product_form = ProductForm(request.POST, prefix='product')
            if product_form.is_valid():
                product_form.save()
                messages.success(request, f"Producto '{product_form.cleaned_data['name']}' guardado exitosamente.")
                return redirect(reverse('stock:manage_stock')) # Redirigir para limpiar forms
            else:
                messages.error(request, "Error al guardar el producto. Revisa los campos.")
                # Los otros forms se re-instancian vacíos

        elif 'submit_stock_entry' in request.POST: # Botón del formulario de remito
            stock_entry_form = StockEntryForm(request.POST, prefix='entry')
            stock_entry_detail_formset = StockEntryDetailFormSet(request.POST, prefix='details')

            if stock_entry_form.is_valid() and stock_entry_detail_formset.is_valid():
                try:
                    with transaction.atomic(): # Asegurar que todo se guarde o nada
                        stock_entry = stock_entry_form.save(commit=False)
                        # Asignar usuario si tienes un campo 'user' o 'created_by' en StockEntry
                        # stock_entry.user = request.user
                        stock_entry.save() # Guardar el encabezado del remito

                        # Guardar los detalles y actualizar stock
                        for form_detail in stock_entry_detail_formset:
                            if form_detail.cleaned_data and not form_detail.cleaned_data.get('DELETE', False):
                                detail = form_detail.save(commit=False)
                                detail.stock_entry = stock_entry # Vincular detalle al encabezado
                                detail.save()

                                # Actualizar stock del producto
                                product_to_update = detail.product
                                product_to_update.stock = F('stock') + detail.quantity
                                product_to_update.save(update_fields=['stock'])
                                # Opcional: Actualizar precio de costo del producto si lo tienes
                                # if detail.purchase_price is not None:
                                #     product_to_update.cost_price = detail.purchase_price
                                #     product_to_update.save(update_fields=['cost_price'])

                        messages.success(request, f"Ingreso de stock #{stock_entry.id} guardado y stock actualizado.")
                        return redirect(reverse('stock:manage_stock'))
                except Exception as e:
                    messages.error(request, f"Error al procesar el ingreso de stock: {str(e)}")
            else:
                messages.error(request, "Error en el formulario de ingreso de stock. Revisa los campos y los detalles.")
                if not stock_entry_detail_formset.is_valid():
                     messages.warning(request, "Asegúrate de que todas las líneas de producto en el remito sean válidas (producto y cantidad).")


    # --- Lógica para GET (y para cuando POST falla y se recarga) ---
    # Búsqueda de productos
    search_query = request.GET.get('q', '')
    products_list = Product.objects.select_related('brand', 'category').order_by('name')
    if search_query:
        products_list = products_list.filter(name__icontains=search_query)
    # Añadir paginación si la lista es muy larga

    # Formularios para creación rápida en modales (para pasarlos al contexto de la plantilla principal)
    category_modal_form = CategoryFormModal()
    brand_modal_form = BrandFormModal()
    supplier_modal_form = SupplierFormModal()

    context = {
        'title': 'Gestión de Inventario',
        'product_form': product_form,
        'stock_entry_form': stock_entry_form,
        'stock_entry_detail_formset': stock_entry_detail_formset,
        'products_list': products_list,
        'search_query': search_query,
        'can_manage_fully': can_manage_fully, # Para mostrar/ocultar secciones en la plantilla
        # Formularios para los modales
        'category_modal_form': category_modal_form,
        'brand_modal_form': brand_modal_form,
        'supplier_modal_form': supplier_modal_form,
    }
    return render(request, 'stock/manage_stock.html', context)