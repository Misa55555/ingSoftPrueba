
# applications/sales/models.py
from django.db import models
from django.conf import settings # Para referenciar al User model
from applications.stock.models import Product # Importa el modelo Product de la app stock
from django.utils import timezone

class Client(models.Model):
    # id_client es automático (id)
    client_name = models.CharField(max_length=150, verbose_name="Nombre")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.client_name

class Sale(models.Model):
    # id_sale es automático (id)
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL, # Si se borra el cliente, la venta queda registrada sin cliente
        null=True,
        blank=True,
        verbose_name="Cliente"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Vincula al modelo User de Django (o tu custom user)
        on_delete=models.SET_NULL, # Si se borra el vendedor, la venta queda sin vendedor asignado
        null=True, # Permite nulo por si acaso, aunque idealmente siempre habrá un user logueado
        verbose_name="Vendedor"
    )
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Venta")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Total")
    # Podrías añadir un campo de estado (e.g., 'procesando', 'completada', 'cancelada')
    # status = models.CharField(max_length=20, default='procesando', ...)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-sale_date']

    def __str__(self):
        client_name = self.client.client_name if self.client else "Consumidor Final"
        return f"Venta #{self.id} - {client_name} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"

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
    # Podrías añadir el subtotal aquí si quieres: quantity * unit_price

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ ${self.unit_price}"

    # Opcional: calcular subtotal
    @property
    def subtotal(self):
        return self.quantity * self.unit_price