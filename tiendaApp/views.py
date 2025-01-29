from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import Categoria, Producto, Imagen, ImagenCategoria, Pedido, TipoPedido
from .serializers import CategoriaSerializer, ProductoSerializer, ImagenSerializer, ImagenCategoriaSerializer, UserSerializer, PedidoSerializer, TipoPedidoSerializer, Transaccion
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

###################################### LOGIN #########################################################

class LoginView(APIView):
    def post(self, request):
        data = request.data
        user = authenticate(username=data['email'], password=data['password'])  # Valida credenciales
        if user:
            token, created = Token.objects.get_or_create(user=user)  # Genera o obtiene el token
            return Response({
                "token": token.key,
                "user_id": user.id  # Incluye el ID del usuario
            })
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

######################################## USUARIO #######################################################

class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  # Busca al usuario por ID
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  # Busca al usuario por ID
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
            user = User.objects.get(id=user_id)  # Busca al usuario por ID
            new_password = request.data.get("new_password")
            if not new_password:
                return Response({"error": "La nueva contraseña es requerida."}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar la contraseña usando `make_password`
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
            # Crear usuario
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
        pedidos = Pedido.objects.filter(idusuario=user)
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, user_id=None):
        user = get_object_or_404(User, id=user_id)
        pedido = get_object_or_404(Pedido, idpedido=pk, idusuario=user)
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data)

    def create(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
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

####################################### TRANSACCIONES #############################################

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = 'TransaccionSerializer'