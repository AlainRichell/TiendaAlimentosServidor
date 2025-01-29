from django.contrib import admin
from django import forms
from .models import Categoria, Producto, Imagen, ImagenCategoria, Pedido, TipoPedido, PedidoProducto, Transaccion, TipoTransaccion
import uuid
from admin_interface.models import Theme
from rest_framework.authtoken.models import TokenProxy

admin.site.site_header = 'Administración de la tienda'
admin.site.index_title = 'Panel de control'
admin.site.site_title = 'Tienda'
admin.site.site_url = 'http://localhost:4200'

admin.site.unregister(Theme)
admin.site.unregister(TokenProxy)

class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1

class ImagenCategoriaInline(admin.TabularInline):
    model = ImagenCategoria
    extra = 1

class TransaccionInline(admin.TabularInline):
    model = Pedido.transacciones.through
    extra = 0

class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'categorias': forms.SelectMultiple(),  # Cambia el widget a SelectMultiple
        }

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('categoria',)
    search_fields = ('categoria',)
    inlines = [ImagenCategoriaInline]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm  # Usamos el nuevo formulario personalizado
    list_display = ('nombre', 'precio', 'cantidad',)
    search_fields = ('nombre', 'descripcion')
    list_filter = ('categorias',)
    inlines = [ImagenInline]
    # Ya no es necesario usar filter_horizontal

#@admin.register(TipoPedido)
#class TipoPedidoAdmin(admin.ModelAdmin):
#    list_display = ('tipopedido',)
#    search_fields = ('tipopedido',)
#
#@admin.register(TipoTransaccion)
#class TipoTransaccionAdmin(admin.ModelAdmin):
#    list_display = ('tipotransaccion',)

class PedidoProductoInline(admin.TabularInline):
    model = PedidoProducto
    extra = 1  # Número de filas adicionales vacías
    fields = ('producto', 'cantidad')  # Mostrar campos directamente editables
    can_delete = True

    def save_new_objects(self, pedido, formset):
        """
        Crea instancias de PedidoProducto automáticamente al guardar productos.
        """
        for form in formset.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):  # Ignorar eliminados
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                
                # Crear automáticamente la relación intermedia PedidoProducto
                PedidoProducto.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                )

    def save_related(self, request, form, formsets, change):
        """
        Sobrescribir save_related para manejar productos directamente.
        """
        super().save_related(request, form, formsets, change)
        pedido = form.instance
        for formset in formsets:
            if isinstance(formset.model, PedidoProducto):
                self.save_new_objects(pedido, formset)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('idusuario', 'idtipopedido', 'fecha')  # Cambiado de 'idusuario' a 'usuario'
    search_fields = ('idusuario__username',)  # Permite buscar por el nombre del usuario
    list_filter = ('idtipopedido', 'fecha')
    date_hierarchy = 'fecha'
    exclude = ('transacciones',)
    inlines = [PedidoProductoInline, TransaccionInline]  # Incluye la nueva configuración del inline

    def save_related(self, request, form, formsets, change):
        """
        Evita duplicar lógica en caso de personalización adicional.
        """
        super().save_related(request, form, formsets, change)

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('idusuario', 'idtransaccion', 'monto', 'moneda', 'fecha', 'hora', 'idtipotransaccion', 'pagodirecto', 'codigoreferencia')
    list_filter = ('fecha', 'idusuario', 'idtipotransaccion', 'moneda', 'pagodirecto')
    search_fields = ('idusuario__username', 'idtransaccion', 'codigoreferencia')