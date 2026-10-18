from django.contrib import admin

from .models import (
    Categoria,
    Cliente,
    DetalleVenta,
    Direccion,
    Producto,
    Proveedor,
    TelefonoCliente,
    Venta,
)

# Permite entrar al admin sin iniciar sesión
admin.site.has_permission = lambda request: True
admin.site.site_header = "Sistema de Ventas"


class SoloLectura:
    """Todos pueden ver; nadie puede agregar, editar ni borrar."""

    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Direccion)
class DireccionAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("calle", "numero", "comuna", "ciudad")
    search_fields = ("calle", "comuna", "ciudad")


@admin.register(Categoria)
class CategoriaAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")


@admin.register(Producto)
class ProductoAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("id", "nombre", "precio_actual", "stock", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("codigo", "nombre", "telefono", "pagina_web", "producto")
    search_fields = ("codigo", "nombre")


class TelefonoInline(SoloLectura, admin.TabularInline):
    model = TelefonoCliente
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("codigo", "nombre", "direccion")
    search_fields = ("codigo", "nombre")
    inlines = [TelefonoInline]


class DetalleInline(SoloLectura, admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ("monto_total",)


@admin.register(Venta)
class VentaAdmin(SoloLectura, admin.ModelAdmin):
    list_display = ("numero_factura", "fecha", "cliente", "descuento", "monto_final")
    list_filter = ("fecha",)
    readonly_fields = ("monto_final",)
    inlines = [DetalleInline]