from rest_framework import serializers
from .models import Categoria, Producto, Imagen, ImagenCategoria

"""
class AfiliadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Afiliado
        fields = ['idafiliado', 'nombre', 'codigo']

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['idmarca', 'marca']

class TallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talla
        fields = ['idtalla', 'talla']
"""


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
