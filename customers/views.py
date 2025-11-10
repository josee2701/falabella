from rest_framework import generics
from rest_framework.views import APIView
from .models import Cliente,TipoDocumento
from .serializers import (
    ClienteListSerializer,
    TipoDocumentoSerializer,
    ClienteReporteFidelizacionSerializer 
)
from django.http import HttpResponse
import pandas as pd
from decimal import Decimal
from io import BytesIO

# --- Imports para cálculos de DB ---
from django.utils import timezone
from datetime import timedelta
from django.db.models import (
    Sum, Q, Value, Case, When, BooleanField, DecimalField
)
from django.db.models.functions import Coalesce
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

class ClienteDownloadReportView(ClienteListView):
    """
    Vista para descargar un reporte de clientes con análisis 
    de fidelización.
    
    Soporta múltiples formatos (csv, xlsx, txt) usando el 
    query param '?format='
    """
    serializer_class = ClienteReporteFidelizacionSerializer

    def get_queryset(self):

        queryset = super().get_queryset()
        today = timezone.now()
        one_month_ago = today - timedelta(days=30)
        monto_mes_q = Sum(
            'compras__total',
            filter=Q(compras__fecha_compra__gte=one_month_ago) & 
                   Q(compras__estado='PAG')
        )
        queryset = queryset.annotate(
            monto_ultimo_mes=Coalesce(
                monto_mes_q, 
                Decimal('0.0'), 
                output_field=DecimalField()
            ),
            aplica_fidelizacion=Case(
                When(monto_ultimo_mes__gt=5_000_000, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        return queryset

    def get(self, request, *args, **kwargs):
        
        queryset = self.get_queryset() 
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        df = pd.DataFrame(data)
        
        column_order = [
            'tipo_documento', 'numero_documento', 'nombre', 'apellido',
            'correo', 'telefono', 'monto_ultimo_mes', 'aplica_fidelizacion'
        ]
        df = df.reindex(columns=[col for col in column_order if col in df.columns])

        export_format = request.query_params.get('formato', 'csv').lower()
        print(export_format)
        
        filename = f"reporte_fidelizacion_clientes_{timezone.now().strftime('%Y%m%d')}"
        print(filename)

        
        if export_format == 'xlsx':
            print('excel')
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            response['Content-Disposition'] = f'attachment; filename="{filename+'1'}.xlsx"'
            print(response)
            return response

        elif export_format == 'txt':
            txt_data = df.to_string(index=False)
            
            response = HttpResponse(txt_data, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}.txt"'
            return response
            
        else:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
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