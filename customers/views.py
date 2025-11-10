from rest_framework import generics
from rest_framework.views import APIView
from .models import Cliente,TipoDocumento
from .serializers import (
    ClienteListSerializer,TipoDocumentoSerializer
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
        queryset = Cliente.objects.filter(activo=True).prefetch_related(
            'documentos__tipo_documento', 
            'telefonos'
        )
        
        tipo_documento = self.request.query_params.get('tipo_documento', None)
        numero_documento = self.request.query_params.get('numero_documento', None)
        

        if tipo_documento:
            queryset = queryset.filter(
                documentos__tipo_documento__id=tipo_documento
            )
            
        if numero_documento:
            queryset = queryset.filter(
                documentos__numero_documento__iexact=numero_documento
            )


        return queryset.distinct()

class ClienteDownloadCSVView(ClienteListView): # <- ¡CAMBIO 1: Hereda de ClienteListView!
    """
    Vista para descargar un reporte de clientes en formato CSV
    utilizando Pandas.
    
    Hereda de ClienteListView para reutilizar su lógica de filtrado.
    """
    
    def get(self, request, *args, **kwargs):
        
        queryset = self.get_queryset() 
        
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
    

class TipoDocumentoListView(generics.ListAPIView):
    """
    API para listar todos los tipos de documento activos.
    Se usa para poblar los menús desplegables en el frontend.
    """
    serializer_class = TipoDocumentoSerializer
    
    def get_queryset(self):
        """
        Retorna solo los tipos de documento que están activos,
        ordenados alfabéticamente por nombre.
        """
        return TipoDocumento.objects.filter(activo=True).order_by('nombre')