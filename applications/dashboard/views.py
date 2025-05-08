from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import time
from decimal import Decimal
from django.db.models import Sum, Count

from applications.sales.models import Sale
from applications.closures.models import CashClosure # Para mostrar el último cierre

@login_required
def dashboard_view(request):
    current_datetime = timezone.now()
    start_of_today = timezone.make_aware(
        timezone.datetime.combine(current_datetime.date(), time.min),
        timezone.get_current_timezone()
    )
    end_of_today = timezone.make_aware(
        timezone.datetime.combine(current_datetime.date(), time.max),
        timezone.get_current_timezone()
    )

    # --- Datos de Ventas del Día ---
    sales_today_qs = Sale.objects.filter(sale_date__gte=start_of_today, sale_date__lte=end_of_today)
    total_sales_amount_today = sales_today_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    sales_count_today = sales_today_qs.count()

    # --- Último Cierre de Caja ---
    last_closure = CashClosure.objects.order_by('-closing_time').first()

    # --- Datos para el Contexto ---
    # Podríamos añadir más adelante: productos con bajo stock, etc.
    active_cash_sales = sales_today_qs.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')


    # Determinar el inicio del período "abierto" actual
    if last_closure:
        current_period_start_time = last_closure.closing_time
    else:
        first_sale_ever = Sale.objects.order_by('sale_date').first()
        current_period_start_time = first_sale_ever.sale_date if first_sale_ever else current_datetime

    # Ventas desde el último cierre (para el resumen de "caja abierta")
    sales_since_last_closure = Sale.objects.filter(
        sale_date__gt=current_period_start_time, # Mayor que el último cierre
        sale_date__lte=current_datetime         # Hasta ahora
    )

    cash_since_last_closure = sales_since_last_closure.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    card_since_last_closure = sales_since_last_closure.filter(payment_method='card').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    transfer_since_last_closure = sales_since_last_closure.filter(payment_method='transfer').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_since_last_closure = cash_since_last_closure + card_since_last_closure + transfer_since_last_closure


    context = {
        'title': 'Panel de Control',
        'total_sales_amount_today': total_sales_amount_today,
        'sales_count_today': sales_count_today,
        'last_closure': last_closure, # Pasamos el objeto completo
        'cash_since_last_closure': cash_since_last_closure,
        'card_since_last_closure': card_since_last_closure,
        'transfer_since_last_closure': transfer_since_last_closure,
        'total_since_last_closure': total_since_last_closure,
        'current_period_start_time' : current_period_start_time,
        'active_cash_sales': active_cash_sales, # Efectivo del día
    }
    return render(request, 'dashboard/home.html', context)