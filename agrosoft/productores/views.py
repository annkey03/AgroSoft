import os
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from .sipsa_service import SipsaService
import random

def obtener_clima_openweather(ciudad, fecha):
    """
    Obtiene datos meteorológicos mediante API de OpenWeatherMap.
    Implementa sistema de fallback para fechas no actuales.
    """
    from datetime import datetime

    hoy = datetime.now().date()
    fecha_consulta = fecha.date() if hasattr(fecha, 'date') else fecha
    diferencia_dias = abs((fecha_consulta - hoy).days)

    if diferencia_dias <= 1:
        api_key = os.getenv("OPENWEATHER_API_KEY")

        if api_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad},CO&appid={api_key}&units=metric&lang=es"

                respuesta = requests.get(url, timeout=10)
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    temperatura = round(datos['main']['temp'], 1)
                    return temperatura
            except requests.RequestException as e:
                pass

    return obtener_clima_simulado(ciudad, fecha)

def obtener_clima_simulado(ciudad, fecha):
    """
    Genera datos climáticos simulados basados en patrones meteorológicos
    de la Sabana de Bogotá con variación estacional y geográfica.
    """
    import random

    temperaturas_base = {
        'Facatativá': 16.5,
        'Madrid': 15.8,
        'Mosquera': 16.8,
        'El Rosal': 14.2,
        'Subachoque': 13.5,
        'Bojacá': 16.3,
        'Funza': 16.1
    }

    mes = fecha.month
    variacion_estacional = {
        1: -2.0, 2: -1.5, 3: 0.0, 4: 1.5, 5: 1.0, 6: -0.5,
        7: -1.5, 8: -1.0, 9: 0.0, 10: 0.8, 11: 0.5, 12: -1.8
    }

    temp_base = temperaturas_base.get(ciudad, 15.5)
    variacion_mes = variacion_estacional.get(mes, 0)

    semilla = hash(f"{ciudad}_{fecha.strftime('%Y-%m-%d')}") % 1000
    random.seed(semilla)
    variacion_diaria = random.uniform(-2.0, 2.0)

    temperatura_final = temp_base + variacion_mes + variacion_diaria
    temperatura_final = round(max(6.0, min(temperatura_final, 28.0)), 1)

    return temperatura_final

def obtener_mensaje_gracioso(max_rentabilidad, municipio, fecha):
    """
    Genera mensajes graciosos cuando las rentabilidades están muy bajas
    """
    # Mensajes según el nivel de rentabilidad
    if max_rentabilidad < 20:
        # Rentabilidades muy bajas (0-20%)
        mensajes_muy_bajos = [
            f"🐄 En {municipio} mejor compra ganado, las vacas no dependen del clima",
            f"🚚 Considera un carrito de comidas en {municipio}, los tacos siempre venden",
            f"🏠 Alquila tu terreno y vete de vacaciones, será más rentable",
            f"🎣 Mejor dedícate a la pesca, los peces no leen el SIPSA",
            f"🍕 Abre una pizzería, la gente siempre tiene hambre",
            f"🚗 Uber en {municipio} puede ser más rentable que sembrar",
            f"💻 Aprende programación, los bugs crecen más rápido que las plantas",
            f"🎪 Monta un circo, será menos riesgoso que la agricultura"
        ]
        return random.choice(mensajes_muy_bajos)

    elif max_rentabilidad < 35:
        # Rentabilidades bajas (20-35%)
        mensajes_bajos = [
            f"🐔 Considera gallinas ponedoras, los huevos no tienen temporada baja",
            f"🏪 Una tienda de barrio en {municipio} podría ser mejor opción",
            f"🚜 Alquila tu tractor a otros, que ellos corran el riesgo",
            f"🌻 Siembra girasoles para selfies, el turismo rural está de moda",
            f"🍯 La apicultura podría ser más dulce que estos números",
            f"🐟 Piscicultura: los peces no protestan por el clima",
            f"🎯 Mejor invierte en un billar, siempre hay clientes",
            f"🏋️ Abre un gimnasio rural, la gente necesita ejercitarse"
        ]
        return random.choice(mensajes_bajos)

    elif max_rentabilidad < 50:
        # Rentabilidades regulares bajas (35-50%)
        mensajes_regulares = [
            f"🤔 En {municipio} tal vez sea mejor esperar una época más favorable",
            f"🌱 Considera cultivos de ciclo corto, menos riesgo y más rotación",
            f"🏡 Huerta casera para autoconsumo y venta local podría funcionar",
            f"🐰 Conejos: se reproducen rápido y no dependen tanto del clima",
            f"🌿 Plantas aromáticas para restaurantes, nicho pequeño pero seguro",
            f"🍄 Hongos comestibles: crecen en cualquier clima controlado",
            f"🎨 Agro-turismo: que otros paguen por ver tu terreno",
            f"📚 Estudia el mercado un poco más, estos números no convencen"
        ]
        return random.choice(mensajes_regulares)

    return None  # No mostrar mensaje si la rentabilidad es >= 50%

def recomendar_productos(request):
    """
    Vista principal para recomendaciones de productos usando datos del SIPSA
    """
    municipios = ['Facatativá', 'Madrid', 'Mosquera', 'El Rosal', 'Subachoque', 'Bojacá', 'Funza']
    fecha_siembra = request.GET.get('fecha')
    ciudad = request.GET.get('municipio', 'Facatativá')

    # Procesar fecha
    if fecha_siembra:
        try:
            fecha_siembra = datetime.strptime(fecha_siembra, "%Y-%m-%d")
        except ValueError:
            fecha_siembra = datetime.now()
    else:
        fecha_siembra = datetime.now()

    # Inicializar servicio SIPSA
    sipsa_service = SipsaService()

    try:
        # Obtener clima primero
        clima = obtener_clima_openweather(ciudad, fecha_siembra)

        # Obtener recomendaciones basadas en municipio, fecha y clima
        recomendaciones = sipsa_service.obtener_productos_recomendados(ciudad, fecha_siembra, clima)

        # Obtener estadísticas del mercado
        estadisticas = sipsa_service.obtener_estadisticas_mercado()

        # Si no hay recomendaciones, mostrar mensaje
        if not recomendaciones:
            return render(request, 'recomendaciones.html', {
                'error': 'No se pudieron obtener datos del SIPSA en este momento. Intente más tarde.',
                'municipios': municipios,
                'municipio_seleccionado': ciudad,
                'fecha_proyeccion': fecha_siembra.strftime('%Y-%m-%d'),
            })

        # Verificar si las rentabilidades están muy bajas para mostrar mensaje gracioso
        mensaje_gracioso = None
        if recomendaciones:
            max_rentabilidad = max(rec['rentabilidad_estimada'] for rec in recomendaciones)
            if max_rentabilidad < 50:  # Si el máximo es menor a 50%
                mensaje_gracioso = obtener_mensaje_gracioso(max_rentabilidad, ciudad, fecha_siembra)

        return render(request, 'recomendaciones.html', {
            'recomendaciones': recomendaciones,
            'estadisticas': estadisticas,
            'fecha_proyeccion': fecha_siembra.strftime('%Y-%m-%d'),
            'metodo_proyeccion': 'Datos oficiales SIPSA-DANE',
            'clima': clima,
            'municipios': municipios,
            'municipio_seleccionado': ciudad,
            'mensaje_gracioso': mensaje_gracioso,
        })

    except Exception as e:
        return render(request, 'recomendaciones.html', {
            'error': f'Error al obtener datos: {str(e)}',
            'municipios': municipios,
            'municipio_seleccionado': ciudad,
            'fecha_proyeccion': fecha_siembra.strftime('%Y-%m-%d'),
        })

def api_precios_sipsa(request):
    """
    API endpoint para obtener precios del SIPSA en formato JSON
    """
    sipsa_service = SipsaService()

    producto = request.GET.get('producto')
    if producto:
        precios = sipsa_service.obtener_precios_por_producto(producto)
    else:
        precios = sipsa_service.obtener_precios_corabastos()

    return JsonResponse({
        'precios': precios[:50],  # Limitar a 50 resultados
        'total': len(precios)
    })