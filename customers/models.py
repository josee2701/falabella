from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class TipoDocumento(models.Model):
    """
    Catálogo de tipos de documentos de identidad
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    def __str__(self):
        return f"{self.nombre}"


class Cliente(models.Model):
    """
    Modelo principal de Cliente con información básica
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name='Apellido'
    )
    correo = models.EmailField(
        unique=True,
        verbose_name='Correo Electrónico'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )


    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Documento(models.Model):
    """
    Modelo para almacenar documentos de identidad del cliente
    Un cliente puede tener múltiples documentos
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Cliente'
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name='documentos',
        verbose_name='Tipo de Documento'
    )
    numero_documento = models.CharField(
        max_length=50,
        verbose_name='Número de Documento'
    )
    principal = models.BooleanField(
        default=False,
        verbose_name='Documento Principal'
    )
    fecha_expedicion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Expedición'
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento'
    )

    def __str__(self):
        return f"{self.tipo_documento.nombre}: {self.numero_documento}"


class TipoTelefono(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del tipo")
    class Meta:
        verbose_name = "Tipo de Teléfono"
        verbose_name_plural = "Tipos de Teléfono"

    def __str__(self):
        return self.nombre
class Telefono(models.Model):
    """
    Modelo para almacenar teléfonos del cliente
    Un cliente puede tener múltiples teléfonos
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='telefonos',
        verbose_name='Cliente'
    )
    phone_type = models.ForeignKey(
        TipoTelefono,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Tipo de Teléfono'
    )
    numero = models.CharField(
        max_length=20,
        verbose_name='Número de Teléfono'
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Extensión'
    )
    principal = models.BooleanField(
        default=False,
        verbose_name='Teléfono Principal'
    )

    class Meta:
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'


    def __str__(self):
        return f"{self.numero} - {self.principal}"


class CategoriaProducto(models.Model):
    """
    Categorías para organizar el catálogo de productos
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Catálogo de productos y servicios disponibles
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código'
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Categoría',
        blank=True,
        null=True
    )
    precio_base = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio Base'
    )
    es_servicio = models.BooleanField(
        default=False,
        verbose_name='Es Servicio',
        help_text='Marcar si es un servicio en lugar de producto físico'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Compra(models.Model):
    """
    Modelo para registrar las compras (Orden de compra/Factura)
    Cabecera de la transacción
    """
    ESTADO_CHOICES = [
        ('PEN', 'Pendiente'),
        ('PAG', 'Pagado'),
        ('CAN', 'Cancelado'),
        ('DEV', 'Devuelto'),
        ('PRO', 'En Proceso'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='compras',
        verbose_name='Cliente'
    )
    numero_factura = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Factura'
    )
    fecha_compra = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Compra'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    estado = models.CharField(
        max_length=3,
        choices=ESTADO_CHOICES,
        default='PEN',
        verbose_name='Estado'
    )
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    impuestos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos (IVA)'
    )
    descuento = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total'
    )
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f"Compra {self.numero_factura} - {self.cliente.nombre} - ${self.total}"



class DetalleCompra(models.Model):
    """
    Detalle de items en cada compra
    Relación muchos a muchos entre Compra y Producto
    """
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Compra'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_compra',
        verbose_name='Producto'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio Unitario'
    )
    descuento_item = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento por Item'
    )
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} "

