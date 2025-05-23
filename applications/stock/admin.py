# applications/stock/admin.py
from django.contrib import admin
from .models import Category, Brand, Supplier, Product, StockEntry, StockEntryDetail

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'email', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'bar_code')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'bar_code', 'brand__name', 'category__name')
    # El stock no debería ser editable directamente aquí si se maneja por remitos,
    # pero lo dejamos visible. Podríamos hacerlo readonly_field si quisiéramos.
    # readonly_fields = ('stock',)
    list_per_page = 20 # Para paginación en la lista

# --- Administración de Ingresos de Stock (Remitos) ---

class StockEntryDetailInline(admin.TabularInline):
    """
    Permite añadir y editar los detalles (productos) de un ingreso de stock
    directamente desde la página del ingreso de stock (StockEntry).
    """
    model = StockEntryDetail
    extra = 1 # Cuántos formularios extra para detalles mostrar por defecto
    autocomplete_fields = ['product'] # Usar autocompletado para el campo producto
    # Definir campos a mostrar en el inline, si es necesario
    # fields = ('product', 'quantity', 'purchase_price')
    # readonly_fields = () # Campos que no se pueden editar en el inline

    # Validar que no se actualice el stock desde el admin directamente aquí,
    # ya que el guardado de StockEntryDetail no actualiza el stock de Product.
    # La actualización de stock de Product se hará desde el formulario de "Cargar Remito" en la vista.

@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'date_received', 'remito_number_display', 'total_items')
    list_filter = ('supplier', 'date_received')
    search_fields = ('id', 'supplier__name', 'remito_number')
    autocomplete_fields = ['supplier'] # Facilita seleccionar proveedor
    inlines = [StockEntryDetailInline] # <-- Aquí se incrustan los detalles
    date_hierarchy = 'date_received'
    list_per_page = 20

    def remito_number_display(self, obj):
        return obj.remito_number if obj.remito_number else "N/A"
    remito_number_display.short_description = "Nro. Remito Prov."

    def total_items(self, obj):
        # Cuenta la cantidad de productos distintos en este ingreso
        return obj.details.count()
    total_items.short_description = "Cant. Items Distintos"

    # Es importante notar que si guardas un StockEntryDetail desde el admin
    # NO se actualizará el stock del producto automáticamente.
    # La lógica de actualización de stock está pensada para el formulario
    # de "Cargar Remito" en la vista principal de stock.
    # Si necesitas que el admin actualice stock, la lógica debería estar en el save()
    # de StockEntryDetail o StockEntry, lo cual puede ser complejo de manejar correctamente
    # para evitar duplicaciones o errores si se edita.

# Opcionalmente, si quieres un admin específico para StockEntryDetail (aunque se maneja mejor con inlines)
# @admin.register(StockEntryDetail)
# class StockEntryDetailAdmin(admin.ModelAdmin):
#     list_display = ('stock_entry', 'product', 'quantity', 'purchase_price')
#     list_filter = ('product', 'stock_entry__supplier')
#     search_fields = ('product__name', 'stock_entry__id')
#     autocomplete_fields = ['stock_entry', 'product']