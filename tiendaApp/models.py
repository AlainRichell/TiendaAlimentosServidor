from django.db import models
import os
from django.dispatch import receiver

"""
class Afiliado(models.Model):
    idafiliado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=8, unique=True)
    def __str__(self):
        return self.nombre
    
class Marca(models.Model):
    idmarca = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=255)

    def __str__(self):
        return self.marca
    
class Talla(models.Model):
    idtalla = models.AutoField(primary_key=True)
    talla = models.CharField(max_length=255)

    def __str__(self):
        return self.talla
"""

class Categoria(models.Model):
    idcategoria = models.AutoField(primary_key=True)
    categoria = models.CharField(max_length=255)

    def __str__(self):
        return self.categoria

class Producto(models.Model):
    idproducto = models.AutoField(primary_key=True)
    categorias = models.ManyToManyField(Categoria, related_name="productos")
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    precio = models.FloatField()
    cantidad = models.IntegerField()
    """
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    talla = models.ManyToManyField(Talla, related_name="productos", blank=True)
    """

    def __str__(self):
        return self.nombre

    def delete(self, *args, **kwargs):
        # Elimina todas las imágenes asociadas cuando se elimina el producto
        for imagen in self.imagenes.all():
            imagen.delete()
        super().delete(*args, **kwargs)

class Imagen(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.idproducto.nombre}"

    def delete(self, *args, **kwargs):
        # Borra el archivo de la imagen cuando se elimine la instancia de Imagen
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

@receiver(models.signals.post_delete, sender=Imagen)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Borra el archivo del sistema cuando se elimina una instancia de Imagen.
    """
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)

class ImagenCategoria(models.Model):
    idcategoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to='categorias/')

    def __str__(self):
        return f"Imagen de {self.idcategoria.categoria}"

    def delete(self, *args, **kwargs):
        # Borra el archivo de la imagen cuando se elimine la instancia de Imagen
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

@receiver(models.signals.post_delete, sender=ImagenCategoria)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Borra el archivo del sistema cuando se elimina una instancia de Imagen.
    """
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)
