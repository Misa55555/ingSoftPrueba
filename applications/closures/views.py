from django.shortcuts import render

# Create your views here.

# applications/closures/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import time # Para definir inicio y fin del día
from django.db.models import Sum, Count
from decimal import Decimal

from applications.sales.models import Sale # Importar modelo Sale
from .models import CashClosure             # Importar modelo CashClosure
from .forms import CashClosureForm          # Importar el formulario



@login_required
def perform_closure_view(request):
    current_datetime = timezone.now() # Hora actual para el FIN del período de este posible cierre

    # --- INICIO: Lógica para determinar el PERÍODO del cierre actual ---
    # Esta lógica se ejecuta tanto para GET (mostrar datos) como para POST (procesar cierre)
    # para asegurar consistencia.

    last_closure = CashClosure.objects.order_by('-closing_time').first()
    # Si necesitas que sea por usuario:
    # last_closure = CashClosure.objects.filter(user=request.user).order_by('-closing_time').first()

    if last_closure:
        # El nuevo período comienza DESPUÉS del cierre anterior
        start_of_period = last_closure.closing_time
    else:
        # No hay cierres previos. El período comienza con la primera venta registrada.
        # O puedes definir una fecha de "inicio del sistema" si lo prefieres.
        first_sale = Sale.objects.order_by('sale_date').first()
        if first_sale:
            start_of_period = first_sale.sale_date
        else:
            # No hay ventas en el sistema, el período es "vacío" hasta ahora.
            start_of_period = current_datetime
    
    end_of_period = current_datetime # El período de ventas a considerar termina AHORA.

    # --- FIN: Lógica para determinar el PERÍODO ---

    # --- Consultar Ventas DEL PERÍODO ACTUAL ---
    # Ventas realizadas >DESPUÉS< del cierre anterior y <=HASTA< ahora.
    sales_in_period = Sale.objects.filter(
        sale_date__gt=start_of_period,  # Mayor que (excluye el instante del cierre anterior)
        sale_date__lte=end_of_period    # Menor o igual que (incluye ventas hasta ahora)
    )
    # Si el cierre es por vendedor, añadir:
    # .filter(seller=request.user) 

    # --- Calcular Totales del Sistema para ESTE PERÍODO ---
    expected_cash = sales_in_period.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_card = sales_in_period.filter(payment_method='card').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_transfer = sales_in_period.filter(payment_method='transfer').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_sales_count = sales_in_period.count()
    grand_total_sales = expected_cash + total_card + total_transfer # Suma de los métodos de pago definidos

    # Esta parte de la lógica (hasta aquí) se ejecuta siempre,
    # tanto para mostrar la página (GET) como para procesar el envío (POST).
    # Esto asegura que 'expected_cash' etc. sean los correctos para el período actual.

    if request.method == 'POST':
        form = CashClosureForm(request.POST)
        if form.is_valid():
            counted_cash_input = form.cleaned_data['counted_cash']
            notes_input = form.cleaned_data['notes']

            # Crear la instancia. El 'opening_time' es el 'start_of_period' que calculamos.
            # El 'closing_time' es el 'end_of_period' (current_datetime cuando se inició la vista).
            closure_instance = CashClosure.objects.create(
                user=request.user,
                opening_time=start_of_period,      # <<< IMPORTANTE
                closing_time=end_of_period,        # <<< IMPORTANTE
                expected_cash=expected_cash,       # Este es el recalculado para el período actual
                total_card_sales=total_card,
                total_transfer_sales=total_transfer,
                grand_total_sales=grand_total_sales,
                total_sales_count=total_sales_count,
                counted_cash=counted_cash_input,
                notes=notes_input
            )
            # El modelo calcula 'cash_difference' en su .save()
            messages.success(request, f"Cierre de caja #{closure_instance.id} realizado. Diferencia: ${closure_instance.cash_difference:,.2f}")
            return redirect(reverse('closures:closure_history'))
    else: # Método GET
        form = CashClosureForm()

    context = {
        'form': form,
        'expected_cash': expected_cash,
        'total_card': total_card,
        'total_transfer': total_transfer,
        'grand_total_sales': grand_total_sales,
        'total_sales_count': total_sales_count,
        'start_of_period_display': start_of_period, # Renombrado para claridad en plantilla
        'end_of_period_display': end_of_period,     # Renombrado para claridad en plantilla
        'title': 'Realizar Cierre de Caja'
    }
    return render(request, 'closures/perform_closure.html', context)


# applications/closures/views.py
# ... (importaciones y vistas existentes) ...

@login_required
def closure_history_view(request):
    # Recuperar todos los cierres, ordenados del más reciente al más antiguo
    # Podrías filtrar por usuario si los cierres son por usuario:
    # closures = CashClosure.objects.filter(user=request.user).order_by('-closing_time')
    closures = CashClosure.objects.all().order_by('-closing_time')

    context = {
        'closures': closures,
        'title': 'Historial de Cierres de Caja'
    }
    return render(request, 'closures/closure_history.html', context)


# applications/closures/views.py
# ... (importaciones y vistas existentes) ...

@login_required
def closure_detail_view(request, closure_id):
    try:
        closure = CashClosure.objects.select_related('user').get(id=closure_id) # Client no está en CashClosure
        # Corrección: Client no está directamente en CashClosure, lo quitamos de select_related por ahora.
        # El usuario (seller) está en las ventas individuales.
        # closure = CashClosure.objects.select_related('user').get(id=closure_id)

        # Recuperar las ventas que ocurrieron DENTRO del período de este cierre específico
        # Usar __gte para opening_time y __lte para closing_time es correcto aquí para incluir los límites.
        sales_in_closure_period = Sale.objects.filter(
            sale_date__gte=closure.opening_time,
            sale_date__lte=closure.closing_time
        ).select_related('client', 'seller').prefetch_related('details__product').order_by('sale_date')
        # Podrías filtrar por el usuario que hizo el cierre si las ventas están asociadas a él
        # y el cierre es personal:
        # .filter(seller=closure.user)

    except CashClosure.DoesNotExist:
        messages.error(request, "El cierre de caja solicitado no existe.")
        return redirect(reverse('closures:closure_history'))

    context = {
        'closure': closure,
        'sales_in_period': sales_in_closure_period,
        'title': f'Detalle del Cierre de Caja #{closure.id}',
        # Datos de empresa para el recibo
        'company_name': "Mi Negocio XYZ (Placeholder)",
        'company_address': "Calle Falsa 123, Ciudad (Placeholder)",
        'company_phone': "+54 9 351 1234567 (Placeholder)",
    }
    return render(request, 'closures/closure_detail.html', context)