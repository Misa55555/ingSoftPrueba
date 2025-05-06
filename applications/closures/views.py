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
    # --- Determinar el período para el cierre: "Hoy" ---
    # Usamos la fecha actual según la zona horaria del proyecto
    current_datetime = timezone.now()
    last_closure = None
    # --- Determinar el período para el cierre ---
    # Busca el último cierre realizado (globalmente o por usuario, según la lógica de negocio)
    # Para este ejemplo, tomaremos el último cierre global.
    last_closure = CashClosure.objects.order_by('-closing_time').first()

    if last_closure:
        start_of_period = last_closure.closing_time
    else:
        # Si no hay cierres previos, tomar desde el inicio de los tiempos o la primera venta
        first_sale = Sale.objects.order_by('sale_date').first()
        if first_sale:
            start_of_period = first_sale.sale_date
        else:
            # Si no hay ventas, el período es "ahora mismo", no habrá ventas que mostrar
            start_of_period = current_datetime

    end_of_period = current_datetime # El cierre es hasta el momento actual
    # --- Consultar Ventas del Período ---
    # Usamos __gt para > start_of_period (no incluir ventas del mismo instante del cierre anterior)
    # y __lte para <= end_of_period
    sales_in_period = Sale.objects.filter(
        sale_date__gt=start_of_period,
        sale_date__lte=end_of_period
    )

    start_of_day = timezone.make_aware(
        timezone.datetime.combine(current_datetime.date(), time.min),
        timezone.get_current_timezone()
    )
    end_of_day = timezone.make_aware(
        timezone.datetime.combine(current_datetime.date(), time.max), # Hasta el final del día
        timezone.get_current_timezone()
    )

    # Alternativa: considerar si ya hubo un cierre hoy para este usuario
    # last_closure_today = CashClosure.objects.filter(user=request.user, closing_time__date=current_datetime.date()).exists()
    # if last_closure_today:
    #     messages.info(request, "Ya se realizó un cierre de caja hoy para este usuario.")
    #     # Podríamos redirigir o mostrar la página de forma diferente

    # --- Consultar Ventas del Período ---
    # Nos aseguramos de que solo se consideren ventas no incluidas en cierres anteriores (si tuviéramos esa lógica)
    # Por ahora, tomamos todas las ventas del día actual.
    sales_in_period = Sale.objects.filter(
        sale_date__gte=start_of_day,
        sale_date__lte=end_of_day
        # Podríamos añadir: seller=request.user si el cierre es por vendedor
    )

    # --- Calcular Totales del Sistema ---
    expected_cash = sales_in_period.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_card = sales_in_period.filter(payment_method='card').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_transfer = sales_in_period.filter(payment_method='transfer').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    # total_other = sales_in_period.filter(payment_method='other_method').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    total_sales_count = sales_in_period.count()
    grand_total_sales = sales_in_period.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    # O sumar los individuales: grand_total_sales = expected_cash + total_card + total_transfer # + total_other

    if request.method == 'POST':
        form = CashClosureForm(request.POST)
        if form.is_valid():
            counted_cash_input = form.cleaned_data['counted_cash']
            notes_input = form.cleaned_data['notes']

            # Guardar el cierre de caja
            # La diferencia se calcula en el método save() del modelo CashClosure
            closure_instance = CashClosure.objects.create(
                user=request.user,
                opening_time=start_of_period, # <-- Guardar el inicio del período
                closing_time=end_of_period, # Guardar el fin del período (hora actual del cierre)
                expected_cash=expected_cash,
                total_card_sales=total_card,
                total_transfer_sales=total_transfer,
                grand_total_sales=grand_total_sales,
                total_sales_count=total_sales_count,
                counted_cash=counted_cash_input,
                notes=notes_input
            )
            # El modelo calcula 'cash_difference' en su .save()
            messages.success(request, f"Cierre de caja #{closure_instance.id} realizado exitosamente. Diferencia de efectivo: ${closure_instance.cash_difference:,.2f}")
            # Redirigir a una vista de detalle del cierre o historial (por ahora al POS)
            # return redirect(reverse('closures:closure_detail', args=[closure_instance.id]))
            return redirect(reverse('closures:closure_history')) # Cambiamos a historial
    
    else: # Método GET
        form = CashClosureForm()

    context = {
        'form': form,
        'expected_cash': expected_cash,
        'total_card': total_card,
        'total_transfer': total_transfer,
        'grand_total_sales': grand_total_sales,
        'total_sales_count': total_sales_count,
        'start_of_period': start_of_period, # Para mostrar en la plantilla
        'end_of_period': end_of_period,     # Para mostrar en la plantilla
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
        closure = CashClosure.objects.select_related('user', 'client').get(id=closure_id) # Client no está en CashClosure
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