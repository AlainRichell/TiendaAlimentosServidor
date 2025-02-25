# Generated by Django 5.1 on 2024-12-13 20:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiendaApp', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('idmarca', models.AutoField(primary_key=True, serialize=False)),
                ('marca', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Talla',
            fields=[
                ('idtalla', models.AutoField(primary_key=True, serialize=False)),
                ('talla', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tiendaApp.marca'),
        ),
        migrations.AddField(
            model_name='producto',
            name='talla',
            field=models.ManyToManyField(blank=True, null=True, related_name='productos', to='tiendaApp.talla'),
        ),
    ]
