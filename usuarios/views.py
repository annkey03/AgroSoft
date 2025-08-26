from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from .forms import AgricultorRegistroForm, SolicitudRecomendacionForm
from .models import SolicitudRecomendacion, Usuario
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import uuid
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.db.models import Count, Sum

# Función auxiliar para verificar si el usuario es admin
def es_admin(user):
    return user.is_authenticated and user.tipo == 'admin'

# Vista del dashboard administrativo
@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    """Vista principal del panel administrativo"""
    # Estadísticas generales
    total_usuarios = Usuario.objects.count()
    total_agricultores = Usuario.objects.filter(tipo='agricultor').count()
    total_solicitudes = SolicitudRecomendacion.objects.count()
    solicitudes_pendientes = SolicitudRecomendacion.objects.filter(estado='pendiente').count()
    
    # Últimas solicitudes
    ultimas_solicitudes = SolicitudRecomendacion.objects.all().order_by('-fecha')[:5]
    
    # Datos para gráficos
    cultivos_populares = SolicitudRecomendacion.objects.values('cultivo_deseado').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_agricultores': total_agricultores,
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'ultimas_solicitudes': ultimas_solicitudes,
        'cultivos_populares': cultivos_populares,
    }
    return render(request, 'admin_dashboard.html', context)

# HU4 - Gestionar usuarios
@login_required
@user_passes_test(es_admin)
def gestionar_usuarios(request):
    """Vista para gestionar usuarios del sistema"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        if 'crear_usuario' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            tipo = request.POST.get('tipo')
            
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                usuario = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    tipo=tipo
                )
                messages.success(request, f'Usuario {username} creado exitosamente.')
                
        elif 'eliminar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                if usuario != request.user:
                    usuario.delete()
                    messages.success(request, 'Usuario eliminado exitosamente.')
                else:
                    messages.error(request, 'No puedes eliminar tu propio usuario.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
    
    context = {
        'usuarios': usuarios
    }
    return render(request, 'gestionar_usuarios.html', context)

# HU8 - Reporte de cultivos
@login_required
@user_passes_test(es_admin)
def reporte_cultivos(request):
    """Vista para generar reportes de cultivos"""
    cultivos = SolicitudRecomendacion.objects.all()
    
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    agricultor = request.GET.get('agricultor')
    cultivo = request.GET.get('cultivo')
    
    if fecha_inicio:
        cultivos = cultivos.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        cultivos = cultivos.filter(fecha__lte=fecha_fin)
    if agricultor:
        cultivos = cultivos.filter(agricultor__username__icontains=agricultor)
    if cultivo:
        cultivos = cultivos.filter(cultivo_deseado__icontains=cultivo)
    
    # Estadísticas
    total_cultivos = cultivos.count()
    total_produccion = cultivos.aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
    context = {
        'cultivos': cultivos,
        'total_cultivos': total_cultivos,
        'total_produccion': total_produccion,
    }
    return render(request, 'reporte_cultivos.html', context)

# HU5 - Reportes gráficos
@login_required
def reportes_graficos(request):
    """Vista para mostrar reportes gráficos"""
    # Datos para gráficos
    cultivos_data = SolicitudRecomendacion.objects.values('cultivo_deseado').annotate(
        total=Count('id'),
        cantidad_total=Sum('cantidad')
    ).order_by('-total')[:10]
    
    # Datos mensuales
    meses = []
    produccion_mensual = []
    for i in range(12):
        mes = datetime.now().replace(month=i+1, day=1)
        meses.append(mes.strftime('%B'))
        produccion = SolicitudRecomendacion.objects.filter(
            fecha__month=i+1,
            fecha__year=datetime.now().year
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        produccion_mensual.append(float(produccion))
    
    # Viabilidad de cultivos
    viabilidad_data = SolicitudRecomendacion.objects.values('viabilidad').annotate(
        total=Count('id')
    )
    
    context = {
        'cultivos_data': list(cultivos_data),
        'meses': meses,
        'produccion_mensual': produccion_mensual,
        'viabilidad_data': list(viabilidad_data),
    }
    return render(request, 'reportes_graficos.html', context)

# HU6 - Producción proyectada
@login_required
@user_passes_test(es_admin)
def produccion_proyectada(request):
    """Vista para calcular producción proyectada"""
    # Primera parte: cálculos básicos
    cultivos_activos = SolicitudRecomendacion.objects.filter(
        estado='procesada'
    ).select_related('agricultor')
    
    # Proyecciones por cultivo
    proyecciones = []
    for cultivo in cultivos_activos:
        if cultivo.cantidad and cultivo.precio_estimado:
            ingreso_proyectado = float(cultivo.cantidad) * float(cultivo.precio_estimado)
            proyecciones.append({
                'cultivo': cultivo,
                'ingreso_proyectado': ingreso_proyectado,
                'rendimiento_estimado': cultivo.cantidad * 0.9  # 90% de rendimiento estimado
            })
    
    context = {
        'proyecciones': proyecciones,
        'total_proyectado': sum(p['ingreso_proyectado'] for p in proyecciones)
    }
    return render(request, 'produccion_proyectada.html', context)

# Resto de las vistas originales...
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
            solicitud.save()
            
            solicitud.recomendacion = recomendacion_completa
            solicitud.fecha_cosecha = fecha_cosecha
            solicitud.dias_cultivo = dias
            solicitud.viabilidad = viabilidad
            solicitud.estado = 'procesada'
            solicitud.save()
            
            return render(request, 'exito.html', {
                'recomendacion': recomendacion_completa,
                'cultivo': cultivo,
                'cantidad': cantidad,
                'fecha_siembra': fecha_siembra,
                'fecha_cosecha': fecha_cosecha,
                'dias': dias,
                'viabilidad': viabilidad,
                'clima': clima
            })
    else:
        form = SolicitudRecomendacionForm()
    
    return render(request, 'recomendacion.html', {'form': form})

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.tipo == 'admin'

@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    if request.user.tipo == 'admin':
        # Si es administrador, mostrar estadísticas generales
        total_usuarios = Usuario.objects.count()
        total_agricultores = Usuario.objects.filter(tipo='agricultor').count()
        total_solicitudes = SolicitudRecomendacion.objects.count()
        solicitudes_pendientes = SolicitudRecomendacion.objects.filter(estado='pendiente').count()
        
        # Obtener las últimas 5 solicitudes (actividad reciente)
        ultimas_solicitudes = SolicitudRecomendacion.objects.select_related('agricultor').order_by('-fecha')[:5]
        
        # Obtener cultivos populares
        cultivos_populares = SolicitudRecomendacion.objects.values('cultivo_deseado').annotate(
            total=Count('id')
        ).order_by('-total')[:5]  # Obtener los 5 cultivos más populares
        
        context = {
            'total_usuarios': total_usuarios,
            'total_agricultores': total_agricultores,
            'total_solicitudes': total_solicitudes,
            'solicitudes_pendientes': solicitudes_pendientes,
            'ultimas_solicitudes': ultimas_solicitudes,
            'cultivos_populares': cultivos_populares,
            'clima_actual': obtener_clima_sabana_occidente()
        }
        return render(request, 'admin_dashboard.html', context)
    
@login_required
@user_passes_test(es_admin)
def gestionar_usuarios(request):
    """Vista para gestionar usuarios del sistema"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        if 'crear_usuario' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            tipo = request.POST.get('tipo')
            
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                usuario = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    tipo=tipo
                )
                messages.success(request, f'Usuario {username} creado exitosamente.')
                
        elif 'eliminar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                if usuario != request.user:
                    usuario.delete()
                    messages.success(request, 'Usuario eliminado exitosamente.')
                else:
                    messages.error(request, 'No puedes eliminar tu propio usuario.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
    
    context = {
        'usuarios': usuarios
    }
    return render(request, 'gestionar_usuarios.html', context)

# HU8 - Reporte de cultivos
@login_required
@user_passes_test(es_admin)
def reporte_cultivos(request):
    """Vista para generar reportes de cultivos"""
    cultivos = SolicitudRecomendacion.objects.all()
    
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    agricultor = request.GET.get('agricultor')
    cultivo = request.GET.get('cultivo')
    
    if fecha_inicio:
        cultivos = cultivos.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        cultivos = cultivos.filter(fecha__lte=fecha_fin)
    if agricultor:
        cultivos = cultivos.filter(agricultor__username__icontains=agricultor)
    if cultivo:
        cultivos = cultivos.filter(cultivo_deseado__icontains=cultivo)
    
    # Estadísticas
    total_cultivos = cultivos.count()
    total_produccion = cultivos.aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
    context = {
        'cultivos': cultivos,
        'total_cultivos': total_cultivos,
        'total_produccion': total_produccion,
    }
    return render(request, 'reporte_cultivos.html', context)

# HU5 - Reportes gráficos
@login_required
@user_passes_test(es_admin)
def reportes_graficos(request):
    """Vista para mostrar reportes gráficos"""
    # Datos para gráficos
    cultivos_data = SolicitudRecomendacion.objects.values('cultivo_deseado').annotate(
        total=Count('id'),
        cantidad_total=Sum('cantidad')
    ).order_by('-total')[:10]
    
    # Datos mensuales
    meses = []
    produccion_mensual = []
    for i in range(12):
        mes = datetime.now().replace(month=i+1, day=1)
        meses.append(mes.strftime('%B'))
        produccion = SolicitudRecomendacion.objects.filter(
            fecha__month=i+1,
            fecha__year=datetime.now().year
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        produccion_mensual.append(float(produccion))
    
    # Viabilidad de cultivos
    viabilidad_data = SolicitudRecomendacion.objects.values('viabilidad').annotate(
        total=Count('id')
    )
    
    context = {
        'cultivos_data': list(cultivos_data),
        'meses': meses,
        'produccion_mensual': produccion_mensual,
        'viabilidad_data': list(viabilidad_data),
    }
    return render(request, 'reportes_graficos.html', context)

# HU6 - Producción proyectada
@login_required
@user_passes_test(es_admin)
def produccion_proyectada(request):
    """Vista para calcular producción proyectada con gráfico de puntos"""
    # Obtener cultivos activos procesados
    cultivos_activos = SolicitudRecomendacion.objects.filter(
        estado='procesada'
    ).select_related('agricultor')
    
    # Proyecciones por cultivo para la tabla
    proyecciones = []
    # Datos para el gráfico de puntos
    datos_grafico = {
        'labels': [],
        'ingresos': [],
        'cantidades': [],
        'colores': []
    }
    
    # Colores para diferentes cultivos
    colores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#8AC926', '#1982C4', '#6A4C93']
    
    for i, cultivo in enumerate(cultivos_activos):
        if cultivo.cantidad and cultivo.precio_estimado:
            ingreso_proyectado = float(cultivo.cantidad) * float(cultivo.precio_estimado)
            rendimiento_estimado = float(cultivo.cantidad) * 0.9
            
            proyecciones.append({
                'cultivo': cultivo,
                'ingreso_proyectado': ingreso_proyectado,
                'rendimiento_estimado': rendimiento_estimado
            })
            
            # Datos para el gráfico de puntos
            datos_grafico['labels'].append(cultivo.cultivo_deseado or 'Sin nombre')
            datos_grafico['ingresos'].append(float(ingreso_proyectado))
            datos_grafico['cantidades'].append(float(cultivo.cantidad))
            datos_grafico['colores'].append(colores[i % len(colores)])
    
    # Calcular estadísticas
    total_proyectado = sum(p['ingreso_proyectado'] for p in proyecciones)
    total_cultivos = len(proyecciones)
    rendimiento_promedio = sum(p['rendimiento_estimado'] for p in proyecciones) / total_cultivos if total_cultivos > 0 else 0
    
    context = {
        'proyecciones': proyecciones,
        'total_proyectado': total_proyectado,
        'total_cultivos': total_cultivos,
        'rendimiento_promedio': rendimiento_promedio,
        'datos_grafico': datos_grafico
    }
    return render(request, 'produccion_proyectada.html', context)

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

def products(request):
    return render(request, 'productos.html')
