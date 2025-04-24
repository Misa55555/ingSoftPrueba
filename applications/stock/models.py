from django.db import models

# Create your models here.

# stock/models.py
from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    unidad = models.CharField(max_length=10)
    vencimiento = models.DateField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
