from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class TipoDocumento(models.Model):
    """
    Catálogo de tipos de documentos de identidad
    """
    TIPO_CHOICES = [
        ('NIT', 'NIT'),
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]

    codigo = models.CharField(
        max_length=3,
        choices=TIPO_CHOICES,
        unique=True,
        verbose_name='Código'
    )
    nombre = models.CharField(
        max_length=100,
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
        db_table = 'tipo_documento'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


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

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['correo']),
            models.Index(fields=['apellido', 'nombre']),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellido}"

    def total_compras_mes_actual(self):
        """
        Calcula el total de compras del cliente en el mes actual
        """
        from django.utils import timezone
        from django.db.models import Sum

        hoy = timezone.now()
        primer_dia_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total = self.compras.filter(
            fecha_compra__gte=primer_dia_mes,
            fecha_compra__lte=hoy
        ).aggregate(total=Sum('monto'))['total']

        return total or Decimal('0.00')

    def es_candidato_fidelizacion(self, monto_minimo=Decimal('1000000.00')):
        """
        Determina si el cliente es candidato a fidelización
        basado en el monto mínimo de compras en el mes actual
        """
        return self.total_compras_mes_actual() >= monto_minimo


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

    class Meta:
        db_table = 'documento'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        unique_together = [['tipo_documento', 'numero_documento']]
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['cliente', 'principal']),
        ]

    def __str__(self):
        return f"{self.tipo_documento.codigo}: {self.numero_documento}"


class Telefono(models.Model):
    """
    Modelo para almacenar teléfonos del cliente
    Un cliente puede tener múltiples teléfonos
    """
    TIPO_TELEFONO_CHOICES = [
        ('CEL', 'Celular'),
        ('FIJ', 'Fijo'),
        ('OFI', 'Oficina'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='telefonos',
        verbose_name='Cliente'
    )
    tipo_telefono = models.CharField(
        max_length=3,
        choices=TIPO_TELEFONO_CHOICES,
        default='CEL',
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
        db_table = 'telefono'
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'
        indexes = [
            models.Index(fields=['cliente', 'principal']),
        ]

    def __str__(self):
        return f"{self.get_tipo_telefono_display()}: {self.numero}"


class Compra(models.Model):
    """
    Modelo para registrar las compras asociadas a cada cliente
    Necesario para calcular la fidelización
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='compras',
        verbose_name='Cliente'
    )
    fecha_compra = models.DateTimeField(
        verbose_name='Fecha de Compra'
    )
    monto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    numero_factura = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Número de Factura'
    )

    class Meta:
        db_table = 'compra'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha_compra']
        indexes = [
            models.Index(fields=['cliente', 'fecha_compra']),
            models.Index(fields=['fecha_compra']),
            models.Index(fields=['numero_factura']),
        ]

    def __str__(self):
        return f"Compra {self.numero_factura or self.id} - {self.cliente.nombre_completo} - ${self.monto}"
