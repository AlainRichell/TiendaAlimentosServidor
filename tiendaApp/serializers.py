from rest_framework import serializers
from .models import Categoria, Producto, Imagen, ImagenCategoria, Profile, User, Pedido, TipoPedido, PedidoProducto, Transaccion, TipoTransaccion

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.save()

        profile.phone = profile_data.get('phone', profile.phone)
        profile.address = profile_data.get('address', profile.address)
        profile.save()

        return instance

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = ['idproducto', 'imagen']

class ImagenCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenCategoria
        fields = ['idcategoria', 'imagen']

class CategoriaSerializer(serializers.ModelSerializer):
    imagenes = ImagenCategoriaSerializer(many=True, read_only=True)
    class Meta:
        model = Categoria
        fields = ['idcategoria', 'categoria', 'imagenes']
        

class ProductoSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True)
    imagenes = ImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'idproducto',
            'categorias',
            'nombre',
            'descripcion',
            'precio',
            'cantidad',
            'imagenes',
        ]

    def create(self, validated_data):
        categorias_data = validated_data.pop('categorias')
        producto = Producto.objects.create(**validated_data)

        for categoria_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(**categoria_data)
            producto.categorias.add(categoria)

        return producto

    def update(self, instance, validated_data):
        categorias_data = validated_data.pop('categorias')

        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.precio = validated_data.get('precio', instance.precio)
        instance.cantidad = validated_data.get('cantidad', instance.cantidad)

        instance.categorias.clear()
        for categoria_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(**categoria_data)
            instance.categorias.add(categoria)

        instance.save()
        return instance

# Serializer para el modelo TipoPedido
class TipoPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPedido
        fields = ['idtipopedido', 'tipopedido']

class PedidoProductoSerializer(serializers.ModelSerializer):
    producto = serializers.StringRelatedField()  # Muestra el nombre del producto
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(), source='producto')

    class Meta:
        model = PedidoProducto
        fields = ['producto_id', 'producto', 'cantidad']

class PedidoSerializer(serializers.ModelSerializer):
    idusuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Relación con User
    idtipopedido = serializers.PrimaryKeyRelatedField(queryset=TipoPedido.objects.all())  # Relación con TipoPedido
    pedido_productos = serializers.SerializerMethodField()
    transacciones = serializers.PrimaryKeyRelatedField(queryset=Transaccion.objects.all(), many=True)

    class Meta:
        model = Pedido
        fields = ['idpedido', 'idusuario', 'pedido_productos', 'idtipopedido', 'fecha', 'transacciones']

    def get_pedido_productos(self, obj):
        return PedidoProductoSerializer(obj.pedido_productos.all(), many=True).data

    def create(self, validated_data):
        pedido_productos_data = validated_data.pop('pedido_productos', [])
        transacciones_data = validated_data.pop('transacciones', [])
        tipo_pedido = validated_data.pop('idtipopedido')

        pedido = Pedido.objects.create(**validated_data, idtipopedido=tipo_pedido)

        for pedido_producto_data in pedido_productos_data:
            producto = pedido_producto_data['producto']
            cantidad = pedido_producto_data['cantidad']
            PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)

        for transaccion in transacciones_data:
            pedido.transacciones.add(transaccion)

        return pedido

    def update(self, instance, validated_data):
        pedido_productos_data = validated_data.pop('pedido_productos', [])
        transacciones_data = validated_data.pop('transacciones', [])
        tipo_pedido = validated_data.pop('idtipopedido', None)

        if tipo_pedido:
            instance.idtipopedido = tipo_pedido

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.pedido_productos.all().delete()
        for pedido_producto_data in pedido_productos_data:
            producto = pedido_producto_data['producto']
            cantidad = pedido_producto_data['cantidad']
            PedidoProducto.objects.create(pedido=instance, producto=producto, cantidad=cantidad)

        instance.transacciones.clear()
        for transaccion in transacciones_data:
            instance.transacciones.add(transaccion)

        return instance

class TransaccionSerializer(serializers.ModelSerializer):
    idusuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    idtipotransaccion = serializers.PrimaryKeyRelatedField(queryset=TipoTransaccion.objects.all())

    class Meta:
        model = Transaccion
        fields = ['idtransaccion', 'idusuario', 'monto', 'moneda', 'hora', 'fecha', 'idtipotransaccion', 'pagodirecto', 'codigoreferencia']