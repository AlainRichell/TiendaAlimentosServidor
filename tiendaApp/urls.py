from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, 
    ProductoViewSet, 
    ImagenViewSet, 
    LoginView, 
    RegisterView, 
    UserDetailView, 
    UserPasswordUpdateView, 
    TipoPedidoViewSet, 
    PedidoViewSet,
    TransaccionViewSet,
    reservar_productos,  # Nueva vista
    confirmar_compra,     # Nueva vista
    cancelar_reserva,
    generate_factura_pdf
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'imagenes', ImagenViewSet)
router.register(r'tipo-pedidos', TipoPedidoViewSet)
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')

# Pedido Views
pedido_list = PedidoViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
pedido_detail = PedidoViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

pedido_cancel = PedidoViewSet.as_view({
    'patch': 'cancelar'
})

urlpatterns = [
    path('', include(router.urls)),
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('user/<int:user_id>/change-password/', UserPasswordUpdateView.as_view(), name='user-change-password'),
    # Rutas de pedidos por usuario
    path('user/<int:user_id>/pedidos/', pedido_list, name='user-pedido-list'),
    path('user/<int:user_id>/pedidos/<int:pk>/', pedido_detail, name='user-pedido-detail'),
    path('user/<int:user_id>/pedidos/<int:pk>/cancelar/', pedido_cancel, name='user-pedido-cancelar'),
    # Rutas generales de pedidos (opcional, para administración o accesos sin filtro de usuario)
    path('pedidos/', pedido_list, name='pedido-list'),
    path('pedidos/<int:pk>/', pedido_detail, name='pedido-detail'),
    path('pedidos/<int:pedido_id>/generate-factura/', generate_factura_pdf, name='generate-factura'),
    # Nuevas rutas para gestión de reservas y compras
    path('reservas/reservar/', reservar_productos, name='reservar-productos'),
    path('reservas/confirmar/', confirmar_compra, name='confirmar-compra'),
    path('reservas/cancelar/', cancelar_reserva, name='cancelar-reserva'),
]
