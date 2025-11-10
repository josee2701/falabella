from django.contrib import admin
from .models import TipoDocumento, Cliente, Documento, Telefono, Compra


class DocumentoInline(admin.TabularInline):
    """Inline para mostrar documentos en el admin de Cliente"""
    model = Documento
    extra = 1
    fields = ('tipo_documento', 'numero_documento', 'principal', 'fecha_expedicion', 'fecha_vencimiento')


class TelefonoInline(admin.TabularInline):
    """Inline para mostrar teléfonos en el admin de Cliente"""
    model = Telefono
    extra = 1
    fields = ('tipo_telefono', 'numero', 'extension', 'principal')


class CompraInline(admin.TabularInline):
    """Inline para mostrar compras en el admin de Cliente"""
    model = Compra
    extra = 0
    fields = ('fecha_compra', 'monto', 'numero_factura', 'descripcion')
    readonly_fields = ('fecha_compra',)


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'correo', 'fecha_registro', 'activo', 'total_compras_actual')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'correo', 'documentos__numero_documento')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion', 'total_compras_actual', 'candidato_fidelizacion')

    inlines = [DocumentoInline, TelefonoInline, CompraInline]

    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'correo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información de Fidelización', {
            'fields': ('total_compras_actual', 'candidato_fidelizacion'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def total_compras_actual(self, obj):
        """Muestra el total de compras del mes actual"""
        return f"${obj.total_compras_mes_actual():,.2f}"
    total_compras_actual.short_description = 'Total Compras Mes Actual'

    def candidato_fidelizacion(self, obj):
        """Indica si el cliente es candidato a fidelización"""
        return obj.es_candidato_fidelizacion()
    candidato_fidelizacion.boolean = True
    candidato_fidelizacion.short_description = 'Candidato Fidelización'


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_documento', 'numero_documento', 'principal', 'fecha_expedicion')
    list_filter = ('tipo_documento', 'principal')
    search_fields = ('numero_documento', 'cliente__nombre', 'cliente__apellido')
    ordering = ('cliente', '-principal')


@admin.register(Telefono)
class TelefonoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_telefono', 'numero', 'extension', 'principal')
    list_filter = ('tipo_telefono', 'principal')
    search_fields = ('numero', 'cliente__nombre', 'cliente__apellido')
    ordering = ('cliente', '-principal')


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'fecha_compra', 'monto')
    list_filter = ('fecha_compra',)
    search_fields = ('numero_factura', 'cliente__nombre', 'cliente__apellido', 'descripcion')
    ordering = ('-fecha_compra',)
    date_hierarchy = 'fecha_compra'

    readonly_fields = ('fecha_compra',)
