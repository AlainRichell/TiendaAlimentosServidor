# Generated by Django 5.1 on 2025-01-21 05:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tiendaApp', '0007_remove_producto_marca_remove_producto_talla'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Afiliado',
        ),
        migrations.DeleteModel(
            name='Marca',
        ),
        migrations.DeleteModel(
            name='Talla',
        ),
    ]
