from django.db import models
from django.contrib.auth.models import User
from Aplicaciones.PalabraInv.models import PalabraInventada

# Create your models here.
class EjemploUso(models.Model):
    palabra = models.ForeignKey(PalabraInventada, on_delete=models.CASCADE, related_name='ejemplos')
    texto = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ejemplo de '{self.palabra}'"
