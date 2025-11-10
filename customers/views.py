from rest_framework import generics
from rest_framework.views import APIView
from .models import Cliente
from .serializers import (
    ClienteListSerializer
)
from django.http import HttpResponse
import pandas as pd  # Importar pandas
class ClienteListView(generics.ListAPIView):
    """
    API para listar todos los clientes activos con su
    información básica (documento y tel principal).
    """
    serializer_class = ClienteListSerializer
    
    def get_queryset(self):

        return Cliente.objects.filter(activo=True).prefetch_related(
            'documentos__tipo_documento', 
            'telefonos'
        )

class ClienteDownloadCSVView(APIView):
    """
    Vista para descargar un reporte de clientes en formato CSV
    utilizando Pandas.
    """
    
    def get(self, request, *args, **kwargs):
        queryset = Cliente.objects.filter(activo=True).prefetch_related(
            'documentos__tipo_documento', 
            'telefonos'
        )
        serializer = ClienteListSerializer(queryset, many=True)
        data = serializer.data
        df = pd.DataFrame(data)
        column_order = [
            'tipo_documento',
            'numero_documento',
            'nombre', 
            'apellido',
            'correo',
            'telefono'
        ]
        df = df.reindex(columns=[col for col in column_order if col in df.columns])

        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_clientes.csv"'
        
        return response