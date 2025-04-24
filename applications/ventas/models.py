from django.db import models

# ---------- MODELOS DE CLIENTE Y VENDEDOR (historial) ----------

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Seller(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    dni = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

# ---------- MODELOS DE CATEGORÍAS Y PRODUCTOS (compras) ----------

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name

# ---------- MODELOS DE VENTAS (ventas) ----------

class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta #{self.id}"

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
