from django.urls import path
from . import views

urlpatterns = [
    path('', views.listarPalabras, name='listarPalabras'),
    path('nueva/', views.nuevaPalabra, name='nuevaPalabra'),
    path('guardar/', views.guardarPalabra, name='guardarPalabra'),
    path('eliminar/<int:id>/', views.eliminarPalabra, name='eliminarPalabra'),
    path('editar/<int:id>/', views.editarPalabra, name='editarPalabra'),
    path('actualizar/<int:id>/', views.actualizarPalabra, name='actualizarPalabra'),
    path('calendario/', views.calendarioPalabras, name='calendarioPalabras'),
    path('eventos/', views.eventosPalabras, name='eventosPalabras'),
]