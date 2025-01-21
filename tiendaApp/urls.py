from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, ImagenViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'imagenes', ImagenViewSet)
"""
router.register(r'afiliados', AfiliadoViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tallas', TallaViewSet)
"""

urlpatterns = [
    path('', include(router.urls)),
]
