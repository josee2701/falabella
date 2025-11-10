from django.urls import path
from . import views

urlpatterns = [

    # API para listar todos los clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente-list'),
    path('clientes/download-csv/', views.ClienteDownloadCSVView.as_view(), name='cliente-download-csv'),
    
]