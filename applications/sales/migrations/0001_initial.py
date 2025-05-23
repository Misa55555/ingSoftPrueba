# Generated by Django 5.2 on 2025-05-01 15:13

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stock', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=150, verbose_name='Nombre')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Dirección')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Venta')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='Monto Total')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.client', verbose_name='Cliente')),
                ('seller', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Vendedor')),
            ],
            options={
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-sale_date'],
            },
        ),
        migrations.CreateModel(
            name='SaleDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Unitario')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stock.product', verbose_name='Producto')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='sales.sale', verbose_name='Venta')),
            ],
            options={
                'verbose_name': 'Detalle de Venta',
                'verbose_name_plural': 'Detalles de Venta',
            },
        ),
    ]
