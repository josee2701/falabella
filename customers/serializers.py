from rest_framework import serializers
from .models import (
    Cliente,
    TipoDocumento
)


class ClienteListSerializer(serializers.ModelSerializer):
    """
    Serializer simple para listar clientes con su
    documento y teléfono principal.
    """
    numero_documento = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    tipo_documento = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'tipo_documento',
            'numero_documento',
            'nombre', 
            'apellido',
            'correo',
            'telefono'
        ]

    def get_documento_principal(self, obj):
        """Helper para obtener el documento prioritario."""
        doc = obj.documentos.filter(principal=True).first()
        
        if not doc:
            doc = obj.documentos.first()
        return doc

    def get_numero_documento(self, obj):
        doc = self.get_documento_principal(obj)
        return doc.numero_documento if doc else None
    
    def get_tipo_documento(self, obj):
        doc = self.get_documento_principal(obj)
        return doc.tipo_documento.nombre if doc and doc.tipo_documento else None

    def get_telefono(self, obj):
        tel = obj.telefonos.filter(principal=True).first()
        
        if not tel:
            tel = obj.telefonos.first()

        return tel.numero if tel else None


class TipoDocumentoSerializer(serializers.ModelSerializer):
    """
    Serializer para listar los tipos de documento.
    Optimizado para un <select> en el frontend.
    """
    class Meta:
        model = TipoDocumento
        fields = ['id', 'nombre']