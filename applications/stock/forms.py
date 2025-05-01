# applications/stock/forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Especifica los campos que quieres incluir en el formulario
        fields = [
            'name',
            'brand',
            'category',
            'description',
            'price',
            'stock',
            'bar_code'
        ]
        # Puedes personalizar widgets si lo necesitas, por ejemplo:
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    # Opcional: Puedes añadir validaciones personalizadas aquí si es necesario
    # def clean_price(self):
    #     price = self.cleaned_data.get('price')
    #     if price <= 0:
    #         raise forms.ValidationError("El precio debe ser mayor que cero.")
    #     return price