from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import Categoria, Producto, Imagen, ImagenCategoria, Pedido, TipoPedido
from .serializers import CategoriaSerializer, ProductoSerializer, ImagenSerializer, ImagenCategoriaSerializer, UserSerializer, PedidoSerializer, TipoPedidoSerializer, Transaccion
from .serializers import TransaccionSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

###################################### LOGIN #########################################################

class LoginView(APIView):
    def post(self, request):
        data = request.data
        user = authenticate(username=data['email'], password=data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id
            })
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

######################################## USUARIO #######################################################

class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

##############################  CAMBIO DE CONTRASEÑA ################################################

class UserPasswordUpdateView(APIView):
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            new_password = request.data.get("new_password")
            if not new_password:
                return Response({"error": "La nueva contraseña es requerida."}, status=status.HTTP_400_BAD_REQUEST)
            
            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Contraseña actualizada con éxito."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

#################################### REGISTRO DE USUARIO ############################################

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create_user(
                username=data['email'],  # Usa el email como username
                email=data['email'],
                password=data['password'],
                first_name=data['fullName']
            )
            # Actualizar el perfil automáticamente creado
            profile = user.profile
            profile.phone = data.get('phone', '')
            profile.address = data.get('address', '')
            profile.save()

            return Response({"message": "Usuario registrado con éxito"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

############################################ CATEGORIA #############################################

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

####################################### PRODUCTOS ##################################################

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
    
@api_view(['POST'])
def reservar_productos(request):
    items = request.data.get('items', [])
    
    for item in items:
        success = Producto.reservar_stock(
            producto_id=item['producto_id'],
            cantidad=item['cantidad']
        )
        if not success:
            # Si falla, libera las reservas previas
            for rollback_item in items[:items.index(item)]:
                Producto.liberar_stock(
                    producto_id=rollback_item['producto_id'],
                    cantidad=rollback_item['cantidad']
                )
            return Response(
                {'error': 'Stock insuficiente para el producto ID: {}'.format(item['producto_id'])},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response({'status': 'Reserva exitosa'})

@api_view(['POST'])
def confirmar_compra(request):
    try:
        items = request.data.get('items', [])
        
        # Validar estructura de los items
        for item in items:
            if 'producto_id' not in item or 'cantidad' not in item:
                return Response(
                    {'error': 'Formato de item inválido. Se requieren "producto_id" y "cantidad"'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            for item in items:
                producto = Producto.objects.select_for_update().get(idproducto=item['producto_id'])
                if not producto.confirmar_compra(item['producto_id'], item['cantidad']):
                    return Response(
                        {'error': f'Error confirmando compra para producto {item["producto_id"]}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response({'status': 'Compra confirmada'})

    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return Response({'error': f'Campo faltante: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def cancelar_reserva(request):
    try:
        items = request.data.get('items', [])
        
        # Validar estructura de los items
        for item in items:
            if 'idproducto' not in item or 'cantidad' not in item:
                return Response(
                    {'error': 'Formato de item inválido. Se requieren "idproducto" y "cantidad"'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            for item in items:
                Producto.liberar_stock(
                    producto_id=item['idproducto'],
                    cantidad=item['cantidad']
                )
            
            return Response({'status': 'Reservas liberadas'})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#################################### IMAGENES DE PRODUCTOS #########################################

class ImagenViewSet(viewsets.ModelViewSet):
    queryset = Imagen.objects.all()
    serializer_class = ImagenSerializer

################################### IMAGENES DE CATEGORIAS ##########################################

class ImagenCategoriaViewSet(viewsets.ModelViewSet):
    queryset = ImagenCategoria.objects.all()
    serializer_class = ImagenCategoriaSerializer

##################################### TIPO O ESTADO DE PEDIDO #######################################

class TipoPedidoViewSet(viewsets.ModelViewSet):
    queryset = TipoPedido.objects.all()
    serializer_class = TipoPedidoSerializer

####################################### PEDIDOS #####################################################

class PedidoViewSet(viewsets.ViewSet):
    def list(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedidos = Pedido.objects.filter(idusuario=user)\
            .prefetch_related('pedido_productos__producto', 'transacciones')\
            .order_by('-idpedido')  # Orden descendente por ID de pedido

        # Si se solicita expansión de relaciones
        expand = request.query_params.get('expand', '')
        if 'productos' in expand:
            pedidos = pedidos.prefetch_related('pedido_productos__producto')
        if 'transacciones' in expand:
            pedidos = pedidos.prefetch_related('transacciones')
            
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedido = get_object_or_404(Pedido, idpedido=pk, idusuario=user)
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data)

    def create(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        
        # Añadir validación manual de productos
        if 'productos' not in request.data or not isinstance(request.data['productos'], list):
            return Response(
                {'productos': ['Este campo es requerido.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PedidoSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(idusuario=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedido = get_object_or_404(Pedido, idpedido=pk, idusuario=user)
        serializer = PedidoSerializer(pedido, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedido = get_object_or_404(Pedido, idpedido=pk, idusuario=user)
        pedido.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['patch'])  # Agregar soporte para GET temporalmente
    def cancelar(self, request, pk=None, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedido = get_object_or_404(Pedido, idpedido=pk, idusuario=user)

        tipo_pedido_cancelado = get_object_or_404(TipoPedido, idtipopedido=4)
        pedido.idtipopedido = tipo_pedido_cancelado
        pedido.save()

        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def generate_factura_pdf(request, pedido_id):
    # Obtener el pedido con todas las relaciones necesarias
    pedido = get_object_or_404(
        Pedido.objects.select_related('idusuario', 'idtipopedido')
                    .prefetch_related('pedido_productos__producto', 'transacciones'),
        idpedido=pedido_id
    )
    
    user = pedido.idusuario
    profile = user.profile  # Asume relación OneToOne con Profile
    
    # Datos del negocio (deberías crear un modelo para esto)
    business_name = "Gustare S.R.L."  # Ejemplo
    business_address = "Av. Principal 123, Ciudad"
    business_tax_id = "RUC-123456789001"
    
    # Calcular detalles de productos
    productos = []
    total_productos = 0
    for pp in pedido.pedido_productos.all():
        producto = pp.producto
        subtotal = pp.cantidad * producto.precio
        total_productos += subtotal
        productos.append({
            'nombre': producto.nombre,
            'cantidad': pp.cantidad,
            'precio_unitario': producto.precio,
            'subtotal': subtotal,
        })
    
    # Obtener datos de transacción
    transaccion = pedido.transacciones.first()
    payment_data = {
        'tipo': transaccion.idtipotransaccion.tipotransaccion if transaccion else "No especificado",
        'referencia': transaccion.codigoreferencia if transaccion else "N/A",
        'total': transaccion.monto if transaccion else total_productos,
        'moneda': transaccion.moneda if transaccion else "USD"
    }
    
    # Contexto para la plantilla
    context = {
        'business': {
            'nombre': business_name,
            'direccion': business_address,
            'ruc': business_tax_id
        },
        'cliente': {
            'nombre': user.get_full_name(),
            'direccion': profile.address,
            'telefono': profile.phone
        },
        'pedido': {
            'numero': pedido.idpedido,
            'fecha': pedido.fecha.strftime("%d/%m/%Y"),
            'estado': pedido.idtipopedido.tipopedido
        },
        'productos': productos,
        'pago': payment_data
    }
    
    # Renderizar HTML a PDF
    html_string = render_to_string('factura_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{pedido.idpedido}.pdf"'
    
    # Generar PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    
    return response

####################################### TRANSACCIONES #############################################

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer