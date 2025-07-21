from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('validar-codigo/<str:email>/', views.validar_codigo, name='validar_codigo'),
    path('nueva-contrasena/<str:email>/<str:codigo>/', views.nueva_contrasena, name='nueva_contrasena'),
]