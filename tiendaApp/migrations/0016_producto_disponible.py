# Generated by Django 5.1 on 2025-02-02 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiendaApp', '0015_rename_transaccion_pedido_transacciones'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='disponible',
            field=models.IntegerField(default=0),
        ),
    ]
