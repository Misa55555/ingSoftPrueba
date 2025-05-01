from django.db import models

# Create your models here.
# applications/stock/models.py

from django.db import models

class Brand(models.Model):
    # id_brand es creado automáticamente por Django como 'id' (AutoField, primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.name

class Category(models.Model):
    # id_cate es creado automáticamente por Django como 'id'
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Product(models.Model):
    # id_prod es creado automáticamente por Django como 'id'
    name = models.CharField(max_length=200, verbose_name="Nombre")
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT, # Evita borrar marca si hay productos asociados
        related_name='products',
        verbose_name="Marca"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # Evita borrar categoría si hay productos asociados
        related_name='products',
        verbose_name="Categoría"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.IntegerField(default=0, verbose_name="Stock Disponible")
    # bar_code es opcional, así que permitimos que sea nulo o vacío
    bar_code = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Código de Barras")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        # Podrías querer ordenar por nombre por defecto
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.brand.name})"