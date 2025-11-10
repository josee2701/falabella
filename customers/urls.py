from django.urls import path
from . import views

urlpatterns = [

    # API para listar todos los clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente-list'),
    path('download/', views.ClienteDownloadReportView.as_view(), name='cliente-download-csv'),
    path('tipos-documento/', views.TipoDocumentoListView.as_view(), name='tipo-documento-list'),
    
]