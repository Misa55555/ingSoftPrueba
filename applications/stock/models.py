# applications/stock/models.py
from django.db import models
from django.utils import timezone # Para default en date_received
from django.core.exceptions import ValidationError # Para validaciones
from decimal import Decimal # Para valores por defecto

# Modelo Category (ya lo tenías, revisamos)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre Categoría")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

# Modelo Brand (ya lo tenías, revisamos)
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre Marca/Fabricante")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['name']

    def __str__(self):
        return self.name

# --- NUEVO/ACTUALIZADO: Modelo Supplier ---
class Supplier(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre Proveedor")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    # podrías añadir cuit = models.CharField(max_length=13, blank=True, null=True, verbose_name="CUIT")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']

    def __str__(self):
        return self.name

# Modelo Product (ya lo tenías, revisamos y ajustamos)
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Artículo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Marca/Fabricante")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoría")
    stock = models.IntegerField(default=0, verbose_name="Stock Actual") # Inicia en 0, se actualiza por remitos
    bar_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código de Barras")
    # podrías añadir:
    # cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Último Precio de Costo")
    # min_stock_level = models.PositiveIntegerField(default=0, verbose_name="Nivel Mínimo de Stock")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.brand.name})"

    def clean(self):
        super().clean()
        if self.price < Decimal('0.00'):
            raise ValidationError({'price': 'El precio de venta no puede ser negativo.'})
        if self.stock < 0: # Aunque se maneje por remitos, una validación extra no daña
            raise ValidationError({'stock': 'El stock no puede ser negativo.'})


# --- NUEVO: Modelo ProductSupplier (Encabezado del Remito de Ingreso) ---
class StockEntry(models.Model): # Renombrado de ProductSupplier para claridad
    remito_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de Remito Prov.")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Proveedor")
    date_received = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Recepción")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas del Ingreso")

    class Meta:
        verbose_name = "Ingreso de Stock (Remito)"
        verbose_name_plural = "Ingresos de Stock (Remitos)"
        ordering = ['-date_received']

    def __str__(self):
        return f"Ingreso #{self.id} - Prov: {self.supplier.name} - Fecha: {self.date_received.strftime('%d/%m/%Y')}"

    # Podríamos tener una propiedad para el total del remito si guardamos precios de compra
    # @property
    # def total_remito_value(self):
    #     return sum(detail.quantity * detail.purchase_price for detail in self.details.all())


# --- NUEVO: Modelo ProductSupplierDetail (Detalle del Remito de Ingreso) ---
class StockEntryDetail(models.Model): # Renombrado de ProductSupplierDetail
    stock_entry = models.ForeignKey(
        StockEntry, # Enlazado al encabezado del remito
        related_name='details', # Para acceder desde StockEntry: my_entry.details.all()
        on_delete=models.CASCADE, # Si se borra el encabezado, se borran los detalles
        verbose_name="Ingreso de Stock"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto Ingresado")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad Ingresada")
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, # Puede ser opcional si no llevas control de costos aquí
        verbose_name="Precio de Compra Unit."
    )

    class Meta:
        verbose_name = "Detalle de Ingreso de Stock"
        verbose_name_plural = "Detalles de Ingresos de Stock"
        # Evitar duplicados del mismo producto en el mismo remito
        unique_together = ('stock_entry', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en Ingreso #{self.stock_entry.id}"

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor que cero.'})
        if self.purchase_price is not None and self.purchase_price < Decimal('0.00'):
            raise ValidationError({'purchase_price': 'El precio de compra no puede ser negativo.'})