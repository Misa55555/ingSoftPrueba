from django.db import models

# Create your models here.
# applications/closures/models.py
from django.db import models
from django.conf import settings # Para el ForeignKey a User
from django.utils import timezone
from decimal import Decimal

class CashClosure(models.Model):
    # --- Información del Cierre ---
    closing_time = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de Cierre")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # O models.PROTECT si no quieres que se borren cierres si se borra el usuario
        null=True, # Permitir nulo si el usuario es borrado y se eligió SET_NULL
        verbose_name="Usuario que Cierra"
    )
    opening_time = models.DateTimeField(verbose_name="Fecha y Hora de Apertura del Período") 

    # --------------------
    closing_time = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de Cierre")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario que Cierra"
    )


    # --- Totales Calculados por el Sistema (basados en ventas del período) ---
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Efectivo Esperado (Sistema)")
    total_card_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Ventas Tarjeta")
    total_transfer_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Ventas Transferencia")
    # total_other_payments = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Otros Pagos") # Para futuro
    grand_total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Total General de Ventas (Calculado)")
    total_sales_count = models.PositiveIntegerField(default=0, verbose_name="Cantidad Total de Ventas")

    # --- Datos Ingresados por el Usuario al Cerrar ---
    counted_cash = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Efectivo Contado en Caja")

    # --- Datos Calculados en el Cierre ---
    cash_difference = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Diferencia de Efectivo")

    # --- Observaciones ---
    notes = models.TextField(blank=True, null=True, verbose_name="Notas / Observaciones")

    class Meta:
        verbose_name = "Cierre de Caja"
        verbose_name_plural = "Cierres de Caja"
        ordering = ['-closing_time']

    def __str__(self):
        user_display = self.user.username if self.user else "N/A"
        return f"Cierre #{self.id} ({self.opening_time.strftime('%d/%m %H:%M')} - {self.closing_time.strftime('%d/%m %H:%M')}) - {user_display}"

    def save(self, *args, **kwargs):
        # Calcular la diferencia de efectivo antes de guardar
        if self.counted_cash is not None and self.expected_cash is not None:
            self.cash_difference = self.counted_cash - self.expected_cash
        super().save(*args, **kwargs)

    # Podríamos añadir propiedades para otros totales si fuera necesario, por ejemplo:
    # @property
    # def total_system_income(self):
    #     return self.expected_cash + self.total_card_sales + self.total_transfer_sales