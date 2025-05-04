# applications/sales/forms.py
from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'client_name',
            'tax_id',
            'tax_condition',
            'address',
            'phone',
            'email'
        ]
        # Puedes añadir widgets para personalizar la apariencia si quieres
        widgets = {
            'client_name': forms.TextInput(attrs={'placeholder': 'Nombre o Razón Social'}),
            'tax_id': forms.TextInput(attrs={'placeholder': 'XX-XXXXXXXX-X'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Dirección Fiscal Completa'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ej: +54 9 351 1234567'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
        }

    # La validación 'clean' del modelo se ejecutará automáticamente
    # al llamar a form.is_valid() si usas ModelForm.
    # Puedes añadir más validaciones específicas del formulario aquí si es necesario.
    # def clean_tax_id(self):
    #     tax_id = self.cleaned_data.get('tax_id')
    #     # ... validación de dígito verificador u otras ...
    #     return tax_id