# compras/forms.py

from django import forms
from applications.stock.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'cantidad', 'unidad', 'vencimiento', 'precio_compra', 'precio_venta']
