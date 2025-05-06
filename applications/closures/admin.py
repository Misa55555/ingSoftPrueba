from django.contrib import admin

# Register your models here.

# applications/closures/admin.py
from django.contrib import admin
from .models import CashClosure

@admin.register(CashClosure)
class CashClosureAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'opening_time',
        'closing_time',
        'user',
        'grand_total_sales',
        'expected_cash',
        'counted_cash',
        'cash_difference'
    )
    list_filter = ('user', 'closing_time')
    search_fields = ('id', 'user__username', 'notes')
    readonly_fields = ( # Campos que se calculan o se ponen automáticamente
        'opening_time',
        'closing_time',
        'user',
        'expected_cash',
        'total_card_sales',
        'total_transfer_sales',
        'grand_total_sales',
        'total_sales_count',
        'cash_difference'
    )
    # Para que en el form del admin solo se puedan editar counted_cash y notes
    # cuando se modifica un cierre (aunque lo ideal es que no se modifiquen mucho post-creación)
    # fields = ('counted_cash', 'notes') # Descomentar si se quiere restringir campos en edición

    def get_form(self, request, obj=None, **kwargs):
        # Al añadir un nuevo cierre desde el admin (poco común, pero posible)
        # solo mostramos los campos que se ingresarían manualmente.
        if obj is None: # Si es un objeto nuevo
            self.fields = ('counted_cash', 'notes') # Solo permitir estos al crear desde admin
            # Podríamos añadir 'user' y 'opening_time'/'closing_time' si queremos
            # que se establezcan manualmente desde el admin, pero es mejor que se
            # generen por la vista 'perform_closure_view'.
            # self.readonly_fields = () # Quitar readonly para creación manual
        else: # Si se está editando
            # Al editar, muchos campos son de solo lectura como se definió arriba.
            # Podemos definir qué campos se muestran y en qué orden
             self.fields = (
                ('opening_time', 'closing_time'),
                'user',
                'total_sales_count',
                'grand_total_sales',
                'expected_cash',
                'total_card_sales',
                'total_transfer_sales',
                'counted_cash',
                'cash_difference',
                'notes'
            )
        return super().get_form(request, obj, **kwargs)