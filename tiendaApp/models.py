from django.db import models
import os
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

################################# ADICIONALES USUARIO CLIENTE #######################################

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

######################################## CATEGORIA ####################################################

class Categoria(models.Model):
    idcategoria = models.AutoField(primary_key=True)
    categoria = models.CharField(max_length=255)

    def __str__(self):
        return self.categoria

########################################### PRODUCTO #################################################

class Producto(models.Model):
    idproducto = models.AutoField(primary_key=True)
    categorias = models.ManyToManyField(Categoria, related_name="productos")
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    precio = models.FloatField()
    cantidad = models.IntegerField()

    def __str__(self):
        return self.nombre

    def delete(self, *args, **kwargs):
        # Elimina todas las imágenes asociadas cuando se elimina el producto
        for imagen in self.imagenes.all():
            imagen.delete()
        super().delete(*args, **kwargs)

#################################### IMAGEN DE PRODUCTO ##############################################

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

################################### IMAGEN DE CATEGORIA ############################################

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
    
########################################## TIPO DE TRANSACCION #########################################

class TipoTransaccion(models.Model):
    idtipotransaccion = models.AutoField(primary_key=True)
    tipotransaccion = models.CharField(max_length=255)

    def __str__(self):
        return self.tipotransaccion

########################################### TRANSACCION ##############################################

class Transaccion(models.Model):
    idtransaccion = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3)  # ISO 4217 format (e.g., USD, EUR)
    hora = models.TimeField()
    fecha = models.DateField()
    idtipotransaccion = models.ForeignKey(TipoTransaccion, on_delete=models.CASCADE, related_name='transacciones')
    pagodirecto = models.BooleanField(default=False)
    codigoreferencia = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Transacción {self.idtransaccion} - Usuario {self.idusuario.username}"

################################## TIPO O ESTADO DE PEDIDO ############################################

class TipoPedido(models.Model):
    idtipopedido = models.AutoField(primary_key=True)
    tipopedido = models.CharField(max_length=255)

    def __str__(self):
        return self.tipopedido

########################################### PEDIDO ####################################################

class Pedido(models.Model):
    idpedido = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='PedidoProducto', related_name='pedidos')
    idtipopedido = models.ForeignKey(TipoPedido, on_delete=models.CASCADE)
    fecha = models.DateField()
    transacciones = models.ManyToManyField(Transaccion, related_name='pedidos')

    def __str__(self):
        return f"Pedido #{self.idpedido} - {self.idusuario.username}"

################################ RELACION DE PRODUCTOS DE UN PEDIDO #####################################

class PedidoProducto(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='pedido_productos')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad})"