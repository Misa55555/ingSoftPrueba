# applications/stock/forms.py
from django import forms
from .models import Product, Category, Brand, Supplier, StockEntry, StockEntryDetail
from django.forms import inlineformset_factory # Para el formset de detalles del remito
from django.utils import timezone


# --- Formularios para Modales (Creación Rápida) ---

class CategoryFormModal(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }

class BrandFormModal(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la marca/fabricante'}),
        }

class SupplierFormModal(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'phone', 'email'] # Considera añadir CUIT si lo tienes en el modelo
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            # 'cuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CUIT del proveedor'}),
        }

# --- Formulario Principal para Cargar Producto ---

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'brand',
            'category',
            'bar_code',
            # 'stock' no se incluye aquí, ya que se maneja por remitos (default=0 en modelo)
            # 'cost_price', # Si decides añadirlo al modelo y quieres poner un costo inicial
            # 'min_stock_level', # Si lo añades al modelo
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Leche Entera 1L'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'brand': forms.Select(attrs={'class': 'form-select select-brand'}), # Clase para JS de modal
            'category': forms.Select(attrs={'class': 'form-select select-category'}), # Clase para JS de modal
            'bar_code': forms.TextInput(attrs={'class': 'form-control'}),
            # 'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            # 'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # Opcional: Si quieres que los campos Select de brand y category
    # muestren una opción vacía como "Seleccionar..."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].empty_label = "Seleccionar Marca..."
        self.fields['category'].empty_label = "Seleccionar Categoría..."
        # El stock se inicializa a 0 por el modelo, no es necesario en el form de alta.
        # Si quisieras ponerlo (aunque no es lo ideal aquí):
        # self.fields['stock'].initial = 0
        # self.fields['stock'].widget = forms.HiddenInput() # O forms.NumberInput(attrs={'readonly': True})


# --- Formulario para Encabezado de Remito (Ingreso de Stock) ---

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ['supplier', 'remito_number', 'date_received', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select select-supplier'}), # Clase para JS de modal
            'remito_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_received': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M' # Formato que espera el input datetime-local
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].empty_label = "Seleccionar Proveedor..."
        if not self.instance.pk: # Si es una nueva instancia
             self.fields['date_received'].initial = timezone.now()


# --- FormSet para Detalles del Remito (Productos Ingresados) ---
# Este formset se usará para agregar múltiples productos a un StockEntry.
StockEntryDetailFormSet = inlineformset_factory(
    StockEntry,  # Modelo Padre
    StockEntryDetail,  # Modelo Hijo (el detalle)
    fields=('product', 'quantity', 'purchase_price'), # Campos a incluir en cada formulario del formset
    extra=1,  # Cuántos formularios extra vacíos mostrar
    can_delete=True, # Permitir borrar formularios del formset (útil para editar)
    widgets={ # Widgets para los campos dentro del formset
        'product': forms.Select(attrs={'class': 'form-select product-select-in-formset', 'required': True}), # Clase para posible JS de búsqueda/autocompletado
        'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'min': '1', 'required': True}),
        'purchase_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01', 'min': '0'}),
    }
)

# Opcional: Modificar los labels de los campos del formset si es necesario
# StockEntryDetailFormSet.form.base_fields['product'].label = "Producto"
# StockEntryDetailFormSet.form.base_fields['quantity'].label = "Cantidad"
# StockEntryDetailFormSet.form.base_fields['purchase_price'].label = "Costo Unit."