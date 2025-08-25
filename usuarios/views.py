

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
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
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

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
    """Vista para solicitar recuperación de contraseña por email"""
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            # Buscar por username o email
            usuario = Usuario.objects.filter(
                models.Q(username=username) | models.Q(email=username)
            ).first()
            
            if not usuario:
                raise Usuario.DoesNotExist
            
            # Generar token y fecha de expiración
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=24)
            
            # Guardar token en la base de datos
            usuario.reset_token = token
            usuario.reset_token_expires = expires_at
            usuario.save()
            
            # Construir URL de reseteo
            reset_url = request.build_absolute_uri(
                reverse('cambiar_contrasena', args=[token])
            )
            
            # Renderizar template de email
            email_html = render_to_string('email_recuperacion.html', {
                'usuario': usuario,
                'reset_url': reset_url
            })
            
            # Enviar email
            send_mail(
                'Recuperación de Contraseña - AgroSoft',
                f'Hola {usuario.username},\n\nPara restablecer tu contraseña, visita: {reset_url}\n\nEste enlace expira en 24 horas.',
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
                html_message=email_html
            )
            
            messages.success(request, 'Se ha enviado un email con instrucciones para restablecer tu contraseña.')
            return redirect('login')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
    
    return render(request, 'recuperar_contrasena.html')

def cambiar_contrasena(request, token):
    """Vista para cambiar la contraseña con token"""
    try:
        usuario = Usuario.objects.get(reset_token=token)
        
        # Verificar si el token es válido
        if not usuario.is_reset_token_valid():
            messages.error(request, 'El enlace de recuperación ha expirado o es inválido.')
            return redirect('recuperar_contrasena')
            
    except Usuario.DoesNotExist:
        messages.error(request, 'El enlace de recuperación es inválido.')
        return redirect('recuperar_contrasena')
    
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'cambiar_contrasena.html', {'token': token})
        
        if len(nueva_contrasena) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'cambiar_contrasena.html', {'token': token})
        
        # ✅ Actualizar contraseña de manera segura
        usuario.set_password(nueva_contrasena)
        usuario.reset_token = None
        usuario.reset_token_expires = None
        usuario.save()
        
        messages.success(request, 'Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.')
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
    
    # Condiciones óptimas por cultivo para Sabana de Occidente
    condiciones_optimas = {
        'maíz': [3, 4, 5, 9, 10, 11],  # Marzo-Mayo, Sept-Nov
        'arroz': [4, 5, 6, 10, 11, 12],  # Abr-Jun, Oct-Dic
        'papa': [1, 2, 3, 7, 8, 9, 10],  # Ene-Mar, Jul-Oct
        'frijol': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Flexible
        'tomate': [2, 3, 4, 8, 9, 10, 11],  # Feb-Abr, Ago-Nov
        'cebolla': [3, 4, 5, 9, 10, 11],  # Mar-Mayo, Sept-Nov
        'zanahoria': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'lechuga': [2, 3, 4, 5, 9, 10, 11],  # Feb-Mayo, Sept-Nov
        'brócoli': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'coliflor': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'aguacate': [3, 4, 5, 9, 10],  # Mar-Mayo, Sept-Oct
        'plátano': [3, 4, 5, 6, 9, 10, 11],  # Mar-Jun, Sept-Nov
        'yuca': [3, 4, 5, 9, 10, 11],  # Mar-Mayo, Sept-Nov
        'arracacha': [2, 3, 4, 8, 9, 10],  # Feb-Abr, Ago-Oct
        'espinaca': [2, 3, 4, 8, 9, 10]  # Feb-Abr, Ago-Oct
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

def obtener_recomendaciones_por_fecha(fecha_siembra):
    """Genera 3 recomendaciones de cultivos basadas en la fecha de siembra"""
    mes = fecha_siembra.month
    
    # Datos de cultivos para la Sabana de Occidente
    cultivos_data = {
        'maíz': {
            'nombre': 'Maíz',
            'dias_cultivo': 90,
            'rendimiento_kg_ha': 8000,
            'precio_kg': 2500,
            'estacion_optima': [3, 4, 5, 9, 10, 11],
            'descripcion': 'Cereal básico, alta demanda en el mercado local',
            'cuidados': 'Requiere buen drenaje y fertilización nitrogenada'
        },
        'papa': {
            'nombre': 'Papa',
            'dias_cultivo': 120,
            'rendimiento_kg_ha': 25000,
            'precio_kg': 2800,
            'estacion_optima': [1, 2, 3, 7, 8, 9, 10],
            'descripcion': 'Tubérculo andino, resistente al frío',
            'cuidados': 'Evitar temperaturas extremas, buena rotación de cultivos'
        },
        'frijol': {
            'nombre': 'Frijol',
            'dias_cultivo': 75,
            'rendimiento_kg_ha': 2500,
            'precio_kg': 4500,
            'estacion_optima': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            'descripcion': 'Leguminosa de alto valor proteico',
            'cuidados': 'Importante para la fijación de nitrógeno en el suelo'
        },
        'tomate': {
            'nombre': 'Tomate',
            'dias_cultivo': 80,
            'rendimiento_kg_ha': 50000,
            'precio_kg': 3500,
            'estacion_optima': [2, 3, 4, 8, 9, 10, 11],
            'descripcion': 'Hortaliza muy demandada, buen precio en mercado',
            'cuidados': 'Requiere tutorado y control de plagas frecuente'
        },
        'cebolla': {
            'nombre': 'Cebolla',
            'dias_cultivo': 110,
            'rendimiento_kg_ha': 20000,
            'precio_kg': 2200,
            'estacion_optima': [3, 4, 5, 9, 10, 11],
            'descripcion': 'Condimento esencial en la cocina colombiana',
            'cuidados': 'Necesita suelo bien preparado y riego controlado'
        },
        'zanahoria': {
            'nombre': 'Zanahoria',
            'dias_cultivo': 90,
            'rendimiento_kg_ha': 30000,
            'precio_kg': 1800,
            'estacion_optima': [2, 3, 4, 8, 9, 10],
            'descripcion': 'Raíz rica en vitamina A, buena conservación',
            'cuidados': 'Suelo suelto y profundo para buen desarrollo'
        },
        'lechuga': {
            'nombre': 'Lechuga',
            'dias_cultivo': 45,
            'rendimiento_kg_ha': 15000,
            'precio_kg': 1500,
            'estacion_optima': [2, 3, 4, 5, 9, 10, 11],
            'descripcion': 'Hortaliza de ciclo corto, alta rotación',
            'cuidados': 'Riego constante, evitar exceso de calor'
        },
        'brócoli': {
            'nombre': 'Brócoli',
            'dias_cultivo': 85,
            'rendimiento_kg_ha': 12000,
            'precio_kg': 4000,
            'estacion_optima': [2, 3, 4, 8, 9, 10],
            'descripcion': 'Vegetal de alto valor nutricional',
            'cuidados': 'Prefiere clima templado, buen manejo de plagas'
        }
    }
    
    # Filtrar cultivos óptimos para la fecha
    cultivos_optimos = []
    for cultivo, data in cultivos_data.items():
        if mes in data['estacion_optima']:
            # Calcular fecha de cosecha
            fecha_cosecha = fecha_siembra + timedelta(days=data['dias_cultivo'])
            
            # Calcular proyecciones
            rendimiento_total = (data['rendimiento_kg_ha'] / 1000) * 100  # Asumiendo 1000m²
            ingreso_proyectado = rendimiento_total * data['precio_kg']
            
            cultivos_optimos.append({
                'cultivo': data['nombre'],
                'dias_cultivo': data['dias_cultivo'],
                'fecha_cosecha': fecha_cosecha,
                'rendimiento_kg': round(rendimiento_total, 2),
                'precio_kg': data['precio_kg'],
                'ingreso_proyectado': round(ingreso_proyectado, 2),
                'descripcion': data['descripcion'],
                'cuidados': data['cuidados'],
                'viabilidad': 'Alta' if mes in data['estacion_optima'] else 'Media'
            })
    
    # Ordenar por viabilidad y rendimiento, tomar top 3
    cultivos_optimos.sort(key=lambda x: (x['viabilidad'] == 'Alta', x['ingreso_proyectado']), reverse=True)
    
    # Si hay menos de 3 óptimos, agregar los mejores disponibles
    if len(cultivos_optimos) < 3:
        todos_cultivos = []
        for cultivo, data in cultivos_data.items():
            fecha_cosecha = fecha_siembra + timedelta(days=data['dias_cultivo'])
            rendimiento_total = (data['rendimiento_kg_ha'] / 1000) * 100
            ingreso_proyectado = rendimiento_total * data['precio_kg']
            
            todos_cultivos.append({
                'cultivo': data['nombre'],
                'dias_cultivo': data['dias_cultivo'],
                'fecha_cosecha': fecha_cosecha,
                'rendimiento_kg': round(rendimiento_total, 2),
                'precio_kg': data['precio_kg'],
                'ingreso_proyectado': round(ingreso_proyectado, 2),
                'descripcion': data['descripcion'],
                'cuidados': data['cuidados'],
                'viabilidad': 'Alta' if mes in data['estacion_optima'] else 'Media'
            })
        
        todos_cultivos.sort(key=lambda x: x['ingreso_proyectado'], reverse=True)
        cultivos_optimos.extend(todos_cultivos[:3-len(cultivos_optimos)])
    
    return cultivos_optimos[:3]

@login_required
def solicitar_recomendacion(request):
    """Vista para solicitar recomendaciones de cultivos"""
    if request.method == 'POST':
        form = SolicitudRecomendacionForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            municipio = form.cleaned_data['municipio']
            fecha_cultivo = form.cleaned_data['fecha_cultivo']
            
            # Generar recomendaciones personalizadas
            recomendaciones = generar_recomendaciones_completas(municipio, fecha_cultivo)
            
            # Guardar solicitud
            solicitud = SolicitudRecomendacion.objects.create(
                agricultor=request.user,
                municipio=municipio,
                fecha_cultivo=fecha_cultivo,
                recomendacion=json.dumps(recomendaciones, default=str),
                estado='completado'
            )
            
            # Renderizar resultados
            return render(request, 'recomendacion_resultado.html', {
                'recomendaciones': recomendaciones,
                'municipio': municipio,
                'fecha_cultivo': fecha_cultivo,
                'clima_actual': obtener_clima_sabana_occidente()
            })
    else:
        form = SolicitudRecomendacionForm()
    
    return render(request, 'recomendacion.html', {
        'form': form,
        'clima_actual': obtener_clima_sabana_occidente()
    })

def generar_recomendaciones_completas(municipio, fecha_siembra):
    """Genera recomendaciones completas basadas en municipio y fecha"""
    mes = fecha_siembra.month
    
    # Datos climáticos por municipio de la Sabana de Occidente
    clima_por_municipio = {
        'chía': {'altitud': 2564, 'temp_media': 14, 'precipitacion': 750},
        'cajicá': {'altitud': 2658, 'temp_media': 13, 'precipitacion': 800},
        'zipaquirá': {'altitud': 2650, 'temp_media': 13, 'precipitacion': 780},
        'facatativá': {'altitud': 2586, 'temp_media': 14, 'precipitacion': 720},
        'soacha': {'altitud': 2565, 'temp_media': 14, 'precipitacion': 700},
    }
    
    # Obtener datos climáticos del municipio
    municipio_lower = municipio.lower().strip()
    clima_data = clima_por_municipio.get(municipio_lower, clima_por_municipio['chía'])
    
    # Precios actualizados de Corabastos (2024)
    precios_corabastos = {
        'maíz': 2800,
        'arroz': 3200,
        'papa': 3000,
        'frijol': 4800,
        'tomate': 3800,
        'cebolla': 2400,
        'zanahoria': 2000,
        'lechuga': 1800,
        'brócoli': 4200,
        'aguacate': 8500,
        'plátano': 1500,
        'yuca': 1400,
        'arracacha': 3800,
        'espinaca': 5000,
        'ajo': 5500,
        'chile': 3500,
        'pepino': 2800,
        'rábano': 2200
    }
    
    # Cultivos recomendados por época y municipio
    cultivos_recomendados = []
    
    # Lógica de selección basada en mes y municipio
    if mes in [12, 1, 2]:  # Invierno seco
        cultivos = [
            {
                'cultivo': 'Papa',
                'dias_cultivo': 120,
                'fecha_cosecha': fecha_siembra + timedelta(days=120),
                'rendimiento_kg': 2500,
                'precio_kg': precios_corabastos['papa'],
                'ingreso_proyectado': 7500000,
                'razon': f'Excelente para {municipio} en invierno seco. Temperatura ideal de {clima_data["temp_media"]}°C',
                'cuidados': 'Evitar heladas, usar abonos orgánicos, rotación de cultivos'
            },
            {
                'cultivo': 'Brócoli',
                'dias_cultivo': 85,
                'fecha_cosecha': fecha_siembra + timedelta(days=85),
                'rendimiento_kg': 1200,
                'precio_kg': precios_corabastos['brócoli'],
                'ingreso_proyectado': 5040000,
                'razon': f'Prefiere clima fresco de {municipio}. Alta demanda en Corabastos',
                'cuidados': 'Control de plagas, riego moderado, cosecha temprana'
            },
            {
                'cultivo': 'Zanahoria',
                'dias_cultivo': 90,
                'fecha_cosecha': fecha_siembra + timedelta(days=90),
                'rendimiento_kg': 3000,
                'precio_kg': precios_corabastos['zanahoria'],
                'ingreso_proyectado': 6000000,
                'razon': f'Raíz perfecta para suelos de {municipio}. Precio estable en Corabastos',
                'cuidados': 'Suelo suelto profundo, evitar exceso de agua'
            }
        ]
    elif mes in [3, 4, 5]:  # Primavera
        cultivos = [
            {
                'cultivo': 'Maíz',
                'dias_cultivo': 90,
                'fecha_cosecha': fecha_siembra + timedelta(days=90),
                'rendimiento_kg': 800,
                'precio_kg': precios_corabastos['maíz'],
                'ingreso_proyectado': 2240000,
                'razon': f'Época ideal para maíz en {municipio}. Alta demanda para arepas y tortillas',
                'cuidados': 'Siembra en surcos, fertilización nitrogenada, control de malezas'
            },
            {
                'cultivo': 'Frijol',
                'dias_cultivo': 75,
                'fecha_cosecha': fecha_siembra + timedelta(days=75),
                'rendimiento_kg': 250,
                'precio_kg': precios_corabastos['frijol'],
                'ingreso_proyectado': 1200000,
                'razon': f'Leguminosa perfecta para rotación en {municipio}. Fija nitrógeno en el suelo',
                'cuidados': 'Siembra en hileras, control de plagas, cosecha cuando vainas estén secas'
            },
            {
                'cultivo': 'Tomate',
                'dias_cultivo': 80,
                'fecha_cosecha': fecha_siembra + timedelta(days=80),
                'rendimiento_kg': 5000,
                'precio_kg': precios_corabastos['tomate'],
                'ingreso_proyectado': 19000000,
                'razon': f'Excelente precio en Corabastos para {municipio}. Alta rotación de mercado',
                'cuidados': 'Tutorado obligatorio, control de plagas, cosecha escalonada'
            }
        ]
    elif mes in [6, 7, 8]:  # Verano lluvioso
        cultivos = [
            {
                'cultivo': 'Yuca',
                'dias_cultivo': 300,
                'fecha_cosecha': fecha_siembra + timedelta(days=300),
                'rendimiento_kg': 1500,
                'precio_kg': precios_corabastos['yuca'],
                'ingreso_proyectado': 2100000,
                'razon': f'Resistente a lluvias en {municipio}. Cultivo seguro para época húmeda',
                'cuidados': 'Drenaje adecuado, control de malezas, cosecha cuando hojas amarilleen'
            },
            {
                'cultivo': 'Arracacha',
                'dias_cultivo': 180,
                'fecha_cosecha': fecha_siembra + timedelta(days=180),
                'rendimiento_kg': 2000,
                'precio_kg': precios_corabastos['arracacha'],
                'ingreso_proyectado': 7600000,
                'razon': f'Raíz andina perfecta para {municipio}. Precio premium en Corabastos',
                'cuidados': 'Suelo bien trabajado, fertilización orgánica, cosecha manual'
            },
            {
                'cultivo': 'Lechuga',
                'dias_cultivo': 45,
                'fecha_cosecha': fecha_siembra + timedelta(days=45),
                'rendimiento_kg': 1500,
                'precio_kg': precios_corabastos['lechuga'],
                'ingreso_proyectado': 2700000,
                'razon': f'Ciclo corto ideal para {municipio}. Múltiples cosechas por año',
                'cuidados': 'Riego controlado, sombra parcial, cosecha temprana'
            }
        ]
    else:  # Otoño (9, 10, 11)
        cultivos = [
            {
                'cultivo': 'Cebolla',
                'dias_cultivo': 110,
                'fecha_cosecha': fecha_siembra + timedelta(days=110),
                'rendimiento_kg': 2000,
                'precio_kg': precios_corabastos['cebolla'],
                'ingreso_proyectado': 4800000,
                'razon': f'Época seca ideal para cebolla en {municipio}. Almacenamiento prolongado',
                'cuidados': 'Siembra en surcos, riego moderado, curado post-cosecha'
            },
            {
                'cultivo': 'Ajo',
                'dias_cultivo': 150,
                'fecha_cosecha': fecha_siembra + timedelta(days=150),
                'rendimiento_kg': 800,
                'precio_kg': precios_corabastos['ajo'],
                'ingreso_proyectado': 4400000,
                'razon': f'Excelente precio en Corabastos para {municipio}. Cultivo de alto valor',
                'cuidados': 'Suelo bien drenado, fertilización fosforada, curado adecuado'
            },
            {
                'cultivo': 'Chile',
                'dias_cultivo': 90,
                'fecha_cosecha': fecha_siembra + timedelta(days=90),
                'rendimiento_kg': 1500,
                'precio_kg': precios_corabastos['chile'],
                'ingreso_proyectado': 5250000,
                'razon': f'Condimento esencial en {municipio}. Demanda constante en Corabastos',
                'cuidados': 'Siembra en hileras, tutorado, cosecha escalonada'
            }
        ]
    
    return cultivos

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
            recomendacion = generar_recomendaciones_completas(cultivo, clima)
            
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

def products(request):
    return render(request, 'productos.html')