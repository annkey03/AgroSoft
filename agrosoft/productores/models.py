from django.db import models

class BoletinPrecios(models.Model):
    fecha = models.DateField()
    archivo_pdf = models.FileField(upload_to='boletines/')
    

    def __str__(self):
        return f"Boletín {self.fecha}"

class Productor(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Cultivo(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    fecha_siembra = models.DateField()
    fecha_cosecha_estimada = models.DateField()
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
