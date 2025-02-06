from rest_framework import serializers
from .models import Categoria, Producto, Imagen, ImagenCategoria, Profile, User, Pedido, TipoPedido, PedidoProducto, Transaccion, TipoTransaccion

################################# ADICIONALES USUARIO CLIENTE #######################################

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

#################################### IMAGEN DE PRODUCTO ##############################################

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = ['idproducto', 'imagen']

################################### IMAGEN DE CATEGORIA ############################################

class ImagenCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenCategoria
        fields = ['idcategoria', 'imagen']

######################################## CATEGORIA ####################################################

class CategoriaSerializer(serializers.ModelSerializer):
    imagenes = ImagenCategoriaSerializer(many=True, read_only=True)
    class Meta:
        model = Categoria
        fields = ['idcategoria', 'categoria', 'imagenes']
        
########################################### PRODUCTO #################################################

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

################################## TIPO O ESTADO DE PEDIDO ############################################

class TipoPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPedido
        fields = ['idtipopedido', 'tipopedido']

################################ RELACION DE PRODUCTOS DE UN PEDIDO #####################################

class PedidoProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(),
        source='producto',  # Mapear producto_id al campo producto
        write_only=True  # Solo para escritura
    )

    class Meta:
        model = PedidoProducto
        fields = ['producto_id', 'producto_nombre', 'cantidad']

########################################### PEDIDO ####################################################

class PedidoSerializer(serializers.ModelSerializer):
    idusuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    idtipopedido = serializers.PrimaryKeyRelatedField(queryset=TipoPedido.objects.all())
    productos = PedidoProductoSerializer(
        many=True,
        source='pedido_productos',
        required=True  # Hacer el campo obligatorio
    )
    transacciones = serializers.PrimaryKeyRelatedField(queryset=Transaccion.objects.all(), many=True)

    class Meta:
        model = Pedido
        fields = ['idpedido', 'idusuario', 'idtipopedido', 'fecha', 'productos', 'transacciones']

    def create(self, validated_data):
        productos_data = validated_data.pop('pedido_productos')
        transacciones_data = validated_data.pop('transacciones', [])
        
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear relaciones de productos
        for producto_data in productos_data:
            PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto_data['producto'],  # Usar el objeto Producto
                cantidad=producto_data['cantidad']
            )
        
        # Agregar transacciones
        pedido.transacciones.set(transacciones_data)
        
        return pedido

    def get_productos(self, obj):
        productos = obj.pedido_productos.all()
        return PedidoProductoSerializer(productos, many=True).data

########################################### TRANSACCION ##############################################

class TransaccionSerializer(serializers.ModelSerializer):
    idusuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    idtipotransaccion = serializers.PrimaryKeyRelatedField(queryset=TipoTransaccion.objects.all())

    class Meta:
        model = Transaccion
        fields = ['idtransaccion', 'idusuario', 'monto', 'moneda', 'hora', 'fecha', 'idtipotransaccion', 'pagodirecto', 'codigoreferencia']