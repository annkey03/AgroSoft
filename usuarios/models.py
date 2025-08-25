from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class Usuario(AbstractUser):
    TIPOS_USUARIO = (
        ('admin', 'Administrador'),
        ('agricultor', 'Agricultor'),
    )
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='agricultor')
    
    # Campos para recuperación de contraseña
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.tipo})"

    def is_reset_token_valid(self):
        """Verifica si el token de reseteo es válido"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        return timezone.now() < self.reset_token_expires

class SolicitudRecomendacion(models.Model):
    agricultor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    cultivo_deseado = models.CharField(max_length=100, blank=True, null=True)
    fecha_cultivo = models.DateField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cantidad en kg")
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Precio estimado por kg")
    ingreso_proyectado = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Ingreso total proyectado")
    recomendacion = models.TextField(blank=True, null=True)
    fecha_cosecha = models.DateField(blank=True, null=True)
    dias_cultivo = models.IntegerField(blank=True, null=True)
    viabilidad = models.CharField(max_length=50, default='pendiente')
    estado = models.CharField(max_length=20, default='pendiente')
    clima_recomendacion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Solicitud de {self.agricultor.username} - {self.municipio} - {self.fecha_cultivo}"
