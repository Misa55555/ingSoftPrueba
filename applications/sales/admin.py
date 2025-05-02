from django.contrib import admin

# Register your models here.
# applications/sales/admin.py
from django.contrib import admin
from .models import Client, Sale, SaleDetail

class SaleDetailInline(admin.TabularInline):
    """Permite ver y editar detalles de venta dentro de la vista de Venta."""
    model = SaleDetail
    extra = 0 # No mostrar formularios extra para añadir detalles por defecto
    readonly_fields = ('product', 'quantity', 'unit_price', 'subtotal') # Hacerlos de solo lectura aquí
    can_delete = False # No permitir borrar detalles desde la venta principal

    def subtotal(self, obj):
        # Si tienes la property @property subtotal en el modelo SaleDetail
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'phone', 'email')
    search_fields = ('client_name', 'email', 'phone')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_date', 'client_display', 'seller', 'total_amount_display')
    list_filter = ('sale_date', 'seller')
    search_fields = ('id', 'client__client_name', 'seller__username')
    readonly_fields = ('sale_date',) # La fecha no se debería cambiar manualmente
    inlines = [SaleDetailInline] # Añadir los detalles aquí

    def client_display(self, obj):
        return obj.client if obj.client else "Consumidor Final"
    client_display.short_description = 'Cliente'

    def total_amount_display(self, obj):
        return f"${obj.total_amount:,.2f}" # Formatear moneda
    total_amount_display.short_description = 'Monto Total'


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    # Generalmente no necesitas acceso directo a SaleDetail aquí si usas inlines
    # Pero si lo quieres:
    list_display = ('id', 'sale', 'product', 'quantity', 'unit_price', 'subtotal_display')
    list_select_related = ('sale', 'product', 'sale__client') # Optimizar consultas
    search_fields = ('sale__id', 'product__name')

    def subtotal_display(self, obj):
         return f"${obj.subtotal:,.2f}"
    subtotal_display.short_description = 'Subtotal'