from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, SolicitudRecomendacion

class AgricultorRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

class SolicitudRecomendacionForm(forms.ModelForm):
    fecha_cultivo = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha exacta de siembra'
    )
    cantidad = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Cantidad a cultivar (kg)',
        min_value=0.1
    )
    
    class Meta:
        model = SolicitudRecomendacion
        fields = ['cultivo_deseado', 'fecha_cultivo', 'cantidad']
        labels = {
            'cultivo_deseado': '¿Qué cultivo deseas sembrar?',
            'fecha_cultivo': 'Fecha exacta de siembra',
            'cantidad': 'Cantidad a cultivar (kg)'
        }
