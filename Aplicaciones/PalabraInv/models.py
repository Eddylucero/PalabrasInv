from django.db import models
from django.contrib.auth.models import User

class PalabraInventada(models.Model):
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    palabra = models.CharField(max_length=100, unique=True)
    significado = models.TextField()
    imagen = models.ImageField(upload_to='palabras/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.palabra
