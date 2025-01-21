from django.contrib import admin
from django import forms
from .models import Categoria, Producto, Imagen, ImagenCategoria
import uuid
from admin_interface.models import Theme

admin.site.site_header = 'Administración de la tienda'
admin.site.index_title = 'Panel de control'
admin.site.site_title = 'Tienda'
admin.site.site_url = 'http://localhost:4200'

#admin.site.unregister(Theme)

"""
@admin.register(Afiliado)
class AfiliadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre',)

    def get_fields(self, request, obj=None):
        if not obj:  # Si se está creando un nuevo afiliado
            return ['nombre']  # Mostrar solo el campo 'nombre'
        else:  # Si se está editando, mostrar 'nombre' y 'codigo'
            return ['nombre', 'codigo']

    def save_model(self, request, obj, form, change):
        if not change:  # Solo si es un nuevo registro
            # Genera un código único
            obj.codigo = self.generate_unique_code()
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si se está editando
            return ['codigo']
        else:
            return []

    # Función para generar un código único
    def generate_unique_code(self):
        import uuid
        while True:
            codigo = str(uuid.uuid4()).split('-')[0]  # Genera un código de 8 caracteres
            if not Afiliado.objects.filter(codigo=codigo).exists():  # Verifica si ya existe
                return codigo

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('marca',)
    search_fields = ('marca',)

@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ('talla',)
    search_fields = ('talla',)
"""


class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1

class ImagenCategoriaInline(admin.TabularInline):
    model = ImagenCategoria
    extra = 1

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