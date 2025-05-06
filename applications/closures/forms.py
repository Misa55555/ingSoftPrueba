# applications/closures/forms.py
from django import forms
from decimal import Decimal
from .models import CashClosure # Aunque no es un ModelForm directo, podemos usarlo para referencia

class CashClosureForm(forms.Form):
    counted_cash = forms.DecimalField(
        label="Efectivo Real Contado en Caja",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00'),
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'})
    )
    notes = forms.CharField(
        label="Notas u Observaciones",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    # Si quisiéramos pasar datos calculados del sistema de forma segura
    # para no recalcularlos en el POST (aunque recalcular es más seguro):
    # expected_cash = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    # total_card_sales = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    # ... y así para otros campos calculados ...