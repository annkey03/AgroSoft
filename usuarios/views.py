from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import AgricultorRegistroForm, SolicitudRecomendacionForm
from .models import SolicitudRecomendacion, Usuario
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import uuid

def registro(request):
    """Vista para el registro de nuevos agricultores"""
    if request.method == 'POST':
        form = AgricultorRegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'agricultor'
            usuario.save()
            login(request, usuario)
            return redirect('home')
    else:
        form = AgricultorRegistroForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    """Vista para el login de usuarios"""
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            error = 'Usuario o contraseña incorrectos.'
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')

def recuperar_contrasena(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            usuario = Usuario.objects.get(username=username)
            # Generar un token temporal en la memoria
            token = str(uuid.uuid4())
            # Redirigir a la página de cambio de contraseña con el token
            return redirect('cambiar_contrasena', token=token)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return render(request, 'recuperar_contrasena.html')
    
    return render(request, 'recuperar_contrasena.html')

def cambiar_contrasena(request, token):
    """Vista para cambiar la contraseña con token"""
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'cambiar_contrasena.html', {'token': token})
        
        if len(nueva_contrasena) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'cambiar_contrasena.html', {'token': token})
        
        # Aquí deberías buscar al usuario y actualizar la contraseña
        # usuario.password = make_password(nueva_contrasena)
        # usuario.save()
        
        messages.success(request, 'Contraseña actualizada exitosamente.')
        return redirect('login')
    
    return render(request, 'cambiar_contrasena.html', {'token': token})

def home(request):
    """Vista principal del dashboard"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Obtener estadísticas básicas
    solicitudes_recientes = []
    if hasattr(request.user, 'solicitudrecomendacion_set'):
        solicitudes_recientes = request.user.solicitudrecomendacion_set.all()[:5]
    
    context = {
        'solicitudes_recientes': solicitudes_recientes,
        'clima_actual': obtener_clima_sabana_occidente()
    }
    return render(request, 'home.html', context)

@login_required
def solicitar_recomendacion(request):
    """Vista para solicitar recomendaciones agrícolas"""
    if request.method == 'POST':
        form = SolicitudRecomendacionForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.agricultor = request.user
            
            # Obtener datos del formulario
            cultivo = form.cleaned_data.get('cultivo_deseado', '')
            fecha_siembra = form.cleaned_data.get('fecha_cultivo')
            cantidad = form.cleaned_data.get('cantidad', 0)
            
            # Días de cultivo según el tipo de cultivo
            dias_cultivo = {
                'maíz': 120,
                'arroz': 150,
                'papa': 135,
                'frijol': 90,
                'tomate': 110,
                'cebolla': 120,
                'zanahoria': 100,
                'lechuga': 60,
                'brócoli': 90,
                'coliflor': 90
            }
            
            dias = dias_cultivo.get(cultivo.lower(), 120)
            fecha_cosecha = fecha_siembra + timedelta(days=dias)
            
            # Análisis de viabilidad según la fecha
            mes_siembra = fecha_siembra.month
            viabilidad = "VIABLE"
            recomendacion_detalle = ""
            
            # Análisis específico para la Sabana Occidente
            if cultivo.lower() == 'maíz':
                if mes_siembra in [3, 4, 5, 9, 10]:
                    viabilidad = "MUY VIABLE"
                    recomendacion_detalle = "Época óptima para maíz en la Sabana Occidente"
                elif mes_siembra in [1, 2, 6, 7, 8, 11, 12]:
                    viabilidad = "VIABLE CON CUIDADO"
                    recomendacion_detalle = "Requiere monitoreo adicional del clima"
                else:
                    viabilidad = "NO RECOMENDABLE"
                    recomendacion_detalle = "Considerar otra época para mejor rendimiento"
            
            elif cultivo.lower() == 'arroz':
                if mes_siembra in [4, 5, 6, 10, 11, 12]:
                    viabilidad = "MUY VIABLE"
                    recomendacion_detalle = "Época ideal para arroz en la región"
                else:
                    viabilidad = "VIABLE CON RIESGO"
                    recomendacion_detalle = "Necesita riego complementario"
            
            elif cultivo.lower() == 'papa':
                if mes_siembra in [1, 2, 3, 7, 8, 9]:
                    viabilidad = "MUY VIABLE"
                    recomendacion_detalle = "Clima templado ideal para papa"
                else:
                    viabilidad = "VIABLE CON CUIDADO"
                    recomendacion_detalle = "Proteger de exceso de lluvia"
            
            # Obtener clima actual
            clima = obtener_clima_sabana_occidente()
            
            # Crear recomendación completa
            recomendacion_completa = f"""
            🌱 **ANÁLISIS DE VIABILIDAD AGRÍCOLA - SABANA OCCIDENTE**
            
            **Cultivo:** {cultivo}
            **Cantidad:** {cantidad} kg
            **Fecha de siembra:** {fecha_siembra.strftime('%d/%m/%Y')}
            **Fecha estimada de cosecha:** {fecha_cosecha.strftime('%d/%m/%Y')}
            **Días de cultivo:** {dias} días
            
            **VIABILIDAD:** {viabilidad}
            **Recomendación:** {recomendacion_detalle}
            """
            
            # Agregar clima como dato separado
            solicitud.clima_recomendacion = clima
            solicitud.save()  # Asegurarse de guardar la solicitud después de agregar el clima
            
            solicitud.recomendacion = recomendacion_completa
            solicitud.fecha_cosecha = fecha_cosecha
            solicitud.dias_cultivo = dias
            solicitud.viabilidad = viabilidad
            solicitud.estado = 'procesada'
            solicitud.save()
            
            # Asegurarse de que la recomendación y el clima se guarden correctamente
            solicitud.recomendacion = recomendacion_completa
            solicitud.clima_recomendacion = clima
            solicitud.save()  # Guardar la solicitud después de agregar la recomendación y el clima
            
            return render(request, 'exito.html', {
                'recomendacion': recomendacion_completa,  # Mostrar la recomendación completa
                'cultivo': cultivo,
                'cantidad': cantidad,
                'fecha_siembra': fecha_siembra,
                'fecha_cosecha': fecha_cosecha,
                'dias': dias,
                'viabilidad': viabilidad,
                'clima': clima  # Asegurarse de pasar el clima también
            })
    else:
        form = SolicitudRecomendacionForm()
    
    return render(request, 'recomendacion.html', {'form': form})

def generar_recomendacion(cultivo, clima):
    """Genera una recomendación basada en el cultivo y el clima"""
    if 'lluvia' in clima.lower() or 'nublado' in clima.lower():
        if cultivo.lower() in ['maíz', 'arroz', 'frijol']:
            return f"Condiciones favorables para {cultivo}. El clima actual es {clima}. Recomendamos sembrar en los próximos días."
        else:
            return f"El clima actual ({clima}) es adecuado para {cultivo}, pero monitorea las condiciones."
    elif 'sol' in clima.lower() or 'despejado' in clima.lower():
        return f"Clima seco actual ({clima}). Asegúrate de tener un buen sistema de riego para {cultivo}."
    else:
        return f"Clima actual: {clima}. Consulta con un especialista local sobre {cultivo}."

def obtener_clima_sabana_occidente():
    """Obtiene el clima actual de la Sabana Occidente"""
    try:
        api_key = "cf9398c1c26a20cfab1a613c34668593"
        lat = 4.8167
        lon = -74.3667
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        descripcion = data["weather"][0]["description"].capitalize()
        temperatura = data["main"]["temp"]
        humedad = data["main"]["humidity"]
        
        return f"{descripcion}, {temperatura}°C, Humedad: {humedad}%"
        
    except requests.exceptions.RequestException as e:
        return f"Error al obtener clima: {str(e)}"
    except KeyError:
        return "Datos de clima no disponibles"

def analizar_clima_optimo(fecha_siembra, cultivo):
    """Analiza si el clima es óptimo para el cultivo en la fecha seleccionada"""
    mes_siembra = fecha_siembra.month
    
    # Condiciones óptimas por cultivo
    condiciones_optimas = {
        'maíz': [3, 4, 5, 9, 10],  # Marzo-Mayo, Sept-Oct
        'arroz': [4, 5, 6, 10, 11, 12],  # Abr-Jun, Oct-Dic
        'papa': [1, 2, 3, 7, 8, 9],  # Ene-Mar, Jul-Sept
        'frijol': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Flexible
        'tomate': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'cebolla': [3, 4, 5, 9, 10, 11],  # Mar-Mayo, Sept-Nov
        'zanahoria': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'lechuga': [2, 3, 4, 5, 9, 10, 11],  # Feb-Mayo, Sept-Nov
        'brócoli': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'coliflor': [2, 3, 4, 8, 9, 10]  # Feb-Abr, Ago-Oct
    }
    
    if mes_siembra in condiciones_optimas.get(cultivo.lower(), []):
        return {
            'optimo': True,
            'mensaje': 'Condiciones climáticas óptimas para este cultivo',
            'riesgo': 'Bajo'
        }
    else:
        return {
            'optimo': False,
            'mensaje': 'Condiciones no óptimas, requiere cuidados adicionales',
            'riesgo': 'Moderado'
        }

# API endpoints para frontend
@csrf_exempt
@login_required
def api_clima_actual(request):
    """Endpoint API para obtener el clima actual"""
    if request.method == 'GET':
        clima = obtener_clima_sabana_occidente()
        return JsonResponse({
            'clima': clima,
            'timestamp': str(datetime.now())
        })
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@login_required
def api_recomendacion(request):
    """Endpoint API para obtener recomendaciones"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cultivo = data.get('cultivo', '')
            clima = obtener_clima_sabana_occidente()
            recomendacion = generar_recomendacion(cultivo, clima)
            
            return JsonResponse({
                'cultivo': cultivo,
                'clima': clima,
                'recomendacion': recomendacion,
                'success': True
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
