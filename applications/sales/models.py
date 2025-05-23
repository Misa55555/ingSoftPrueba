
# applications/sales/models.py
from django.db import models
from django.conf import settings # Para referenciar al User model
from applications.stock.models import Product # Importa el modelo Product de la app stock
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

cuit_cuil_validator = RegexValidator(
    regex=r'^\d{2}-\d{8}-\d{1}$',
    message="El formato debe ser XX-XXXXXXXX-X."
)

class Client(models.Model):
    # --- Choices para Condición frente al IVA ---
    TAX_CONDITION_CHOICES = [
        ('CF', 'Consumidor Final'),
        ('RI', 'Responsable Inscripto'),
        ('MO', 'Monotributista'),
        ('EX', 'Exento'),
        # Añadir otros si son necesarios
    ]

    client_name = models.CharField(max_length=150, verbose_name="Nombre o Razón Social")
    # CUIT/CUIL - Hacerlo unico y opcional (un Consumidor Final puede no tenerlo registrado)
    tax_id = models.CharField(
        max_length=13, # Formato XX-XXXXXXXX-X
        unique=True,
        null=True, # Permitir nulo
        blank=True, # Permitir vacío en formularios
        validators=[cuit_cuil_validator],
        verbose_name="CUIT/CUIL"
    )
    tax_condition = models.CharField(
        max_length=2,
        choices=TAX_CONDITION_CHOICES,
        default='CF', # Default a Consumidor Final
        verbose_name="Condición IVA"
    )
    address = models.TextField(blank=True, null=True, verbose_name="Dirección Fiscal")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")


    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['client_name']

    def __str__(self):
        base = self.client_name
        if self.tax_id:
            base += f" ({self.tax_id})"
        return base

    def clean(self):
        # Validación: Si no es Consumidor Final, CUIT/CUIL debería ser obligatorio
        if self.tax_condition != 'CF' and not self.tax_id:
            raise ValidationError({'tax_id': 'El CUIT/CUIL es requerido para esta condición de IVA.'})
        # Asegurarse que si es Consumidor Final, no tenga CUIT/CUIL (o manejarlo segun reglas AFIP)
        # if self.tax_condition == 'CF' and self.tax_id:
        #     raise ValidationError({'tax_id': 'Un Consumidor Final no debería tener CUIT/CUIL asociado.'})
        pass 

class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
    ]

    # --- Campos Principales ---
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Vendedor"
    )
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Venta")

    # --- Campos de Montos ---
    # total_amount almacena el MONTO FINAL (después de descuentos)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        verbose_name="Monto Total (Final)"
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        verbose_name="Monto Descuento"
    )

    # --- Campos de Pago ---
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name="Método de Pago"
    )
    amount_received = models.DecimalField( # Específico para efectivo
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="Monto Recibido (Efectivo)"
    )
    change_given = models.DecimalField( # Específico para efectivo
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="Cambio Entregado (Efectivo)"
    )

    # --- Campos Adicionales ---
    discount_reason = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Razón Descuento"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    # --- Meta Clase  ---
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-sale_date']

    # --- Propiedad Subtotal (sin cambios) ---
    @property
    def subtotal(self):
        if self.total_amount is not None and self.discount_amount is not None:
             # El subtotal es el total final MÁS el descuento que se aplicó
             return self.total_amount + self.discount_amount
        return self.total_amount # Fallback

    # --- Método __str__  ---
    def __str__(self):
        client_name = self.client.client_name if self.client else "Consumidor Final"
        return f"Venta #{self.id} - {client_name} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"

    # --- Método clean (Corregido indentación y validación) ---
    def clean(self):
        # Validación de Descuento 
        if self.discount_amount < 0:
            raise ValidationError({'discount_amount': 'El descuento no puede ser negativo.'})

        # También es mejor validar la suficiencia del monto recibido en la VISTA.
        # Aquí podríamos validar que si hay cambio, no sea negativo.
        if self.change_given is not None and self.change_given < 0:
             raise ValidationError({'change_given': 'El cambio no puede ser negativo.'})

    # --- Método save (Corregido indentación, quitado cálculo de cambio) ---
    def save(self, *args, **kwargs):
        # Quitamos el cálculo automático de 'change_given'.
        # Este cálculo es más seguro hacerlo en la vista 'checkout_view'
        # ANTES de crear el objeto Sale, porque ahi tenemos acceso fácil
        # al subtotal, descuento y monto recibido validados.
        super().save(*args, **kwargs) # Llamar al método save original

        #tengo que ver si añadir esto
        # def __str__(self):  
        #     client_name = self.client.client_name if self.client else "Consumidor Final"
        #     return f"Venta #{self.id} - {client_name} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"
        #     super().save(*args, **kwargs)
    

class SaleDetail(models.Model):
    # id_sale_details es automático (id)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE, # Si se borra la venta, se borran sus detalles
        related_name='details', # Para acceder desde la venta: venta.details.all()
        verbose_name="Venta"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT, # No permite borrar un producto si está en detalles de venta
        verbose_name="Producto"
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    # Guarda el precio al momento de la venta, porque el precio del producto puede cambiar
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    # se podria añadir el subtotal  quantity * unit_price

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ ${self.unit_price}"

    # Opcional: calcular subtotal
    @property
    def subtotal(self):
        return self.quantity * self.unit_price