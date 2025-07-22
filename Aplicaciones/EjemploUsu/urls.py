from django.urls import path
from . import views

urlpatterns = [
    path('', views.listarEjemplos, name='listarEjemplos'),
    path('nueva/', views.nuevoEjemplo, name='nuevoEjemplo'),
    path('guardar/', views.guardarEjemplo, name='guardarEjemplo'),
    path('editar/<int:id>/', views.editarEjemplo, name='editarEjemplo'),
    path('actualizar/<int:id>/', views.actualizarEjemplo, name='actualizarEjemplo'),
    path('eliminar/<int:id>/', views.eliminarEjemplo, name='eliminarEjemplo'),
    path('telegram/<int:pk>/', views.envio_telegram, name='envio_telegram'),
    path('procesar-mensaje-telegram/', views.procesar_mensaje_telegram, name='procesar_mensaje_telegram'),
    path('ayuda-telegram/', views.ayuda_telegram, name='ayuda_telegram'),
    
    # Nuevas rutas para gráficos simplificadas
    path('graficos/', views.graficos_ejemplos, name='graficos_ejemplos'),
    path('datos-graficos/', views.datos_graficos_ejemplos, name='datos_graficos_ejemplos'),
]