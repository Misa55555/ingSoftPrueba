
# Register your models here.
# applications/stock/admin.py
from django.contrib import admin
from .models import Brand, Category, Product

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'bar_code')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'description', 'bar_code')
    # Para campos ForeignKey, es útil tener autocompletado si hay muchos
    # raw_id_fields = ('brand', 'category',) # Opcional
    autocomplete_fields = ('brand', 'category') # Preferido si usas Django >= 2.0