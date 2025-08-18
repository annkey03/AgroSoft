from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Usuario(AbstractUser):
    TIPOS_USUARIO = (
        ('admin', 'Administrador'),
        ('agricultor', 'Agricultor'),
    )
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='agricultor')

    def __str__(self):
        return f"{self.username} ({self.tipo})"

class SolicitudRecomendacion(models.Model):
    agricultor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    fecha_cultivo = models.DateField(help_text="Fecha de siembra")
    recomendacion = models.TextField(blank=True, null=True)
    fecha_cosecha = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')
    
    def __str__(self):
        return f"Solicitud de {self.agricultor.username} - {self.municipio} - {self.fecha_cultivo}"
