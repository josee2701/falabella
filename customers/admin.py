from django.contrib import admin
from .models import (
    TipoDocumento,
    Cliente,
    Documento,
    TipoTelefono,
    Telefono,
    CategoriaProducto,
    Producto,
    Compra,
    DetalleCompra
)

admin.site.register(TipoDocumento)
admin.site.register(Cliente)
admin.site.register(Documento)
admin.site.register(TipoTelefono)
admin.site.register(Telefono)
admin.site.register(CategoriaProducto)
admin.site.register(Producto)
admin.site.register(Compra)
admin.site.register(DetalleCompra)