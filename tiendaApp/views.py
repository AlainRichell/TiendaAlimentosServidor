from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Categoria, Producto, Imagen, ImagenCategoria
from .serializers import CategoriaSerializer, ProductoSerializer, ImagenSerializer, ImagenCategoriaSerializer

"""
class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

class TallaViewSet(viewsets.ModelViewSet):
    queryset = Talla.objects.all()
    serializer_class = TallaSerializer

class AfiliadoViewSet(viewsets.ModelViewSet):
    queryset = Afiliado.objects.all()
    serializer_class = AfiliadoSerializer
    
    @action(detail=False, methods=['get'], url_path='codigo/(?P<codigo>[^/.]+)')
    def retrieve_by_codigo(self, request, codigo=None):
        try:
            afiliado = Afiliado.objects.get(codigo=codigo)
            serializer = AfiliadoSerializer(afiliado)
            return Response(serializer.data)
        except Afiliado.DoesNotExist:
            return Response({'error': 'Afiliado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
"""

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ImagenViewSet(viewsets.ModelViewSet):
    queryset = Imagen.objects.all()
    serializer_class = ImagenSerializer

class ImagenCategoriaViewSet(viewsets.ModelViewSet):
    queryset = ImagenCategoria.objects.all()
    serializer_class = ImagenCategoriaSerializer