from django.urls import path
from . import views

urlpatterns = [
    path('', views.listarEjemplos, name='listarEjemplos'),
    path('nueva/', views.nuevoEjemplo, name='nuevoEjemplo'),
    path('guardar/', views.guardarEjemplo, name='guardarEjemplo'),
    path('editar/<int:id>/', views.editarEjemplo, name='editarEjemplo'),
    path('actualizar/<int:id>/', views.actualizarEjemplo, name='actualizarEjemplo'),
    path('eliminar/<int:id>/', views.eliminarEjemplo, name='eliminarEjemplo'),
]
