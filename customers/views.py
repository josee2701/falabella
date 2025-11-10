from rest_framework import generics
from .models import Cliente
from .serializers import (
    ClienteListSerializer
)
class ClienteListView(generics.ListAPIView):
    """
    API para listar todos los clientes activos con su
    información básica (documento y tel principal).
    """
    serializer_class = ClienteListSerializer
    
    def get_queryset(self):
        # Optimizamos la consulta para evitar N+1 queries
        # al acceder a 'documentos' y 'telefonos' en el serializer.
        return Cliente.objects.filter(activo=True).prefetch_related(
            'documentos__tipo_documento', # Incluimos tipo_documento en el prefetch
            'telefonos'
        )