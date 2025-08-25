from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, SolicitudRecomendacion

class AgricultorRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
           super(AgricultorRegistroForm, self).__init__(*args, **kwargs)
           self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
           self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
           self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
           self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar contraseña'

class SolicitudRecomendacionForm(forms.ModelForm):
    municipio = forms.CharField(
        max_length=100,
        label='Municipio de siembra',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Madrid, Facatativa, Mosquera'})
    )
    fecha_cultivo = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de siembra'
    )
    
    class Meta:
        model = SolicitudRecomendacion
        fields = ['municipio', 'fecha_cultivo']
        labels = {
            'municipio': 'Municipio de siembra',
            'fecha_cultivo': 'Fecha de siembra'
        }
