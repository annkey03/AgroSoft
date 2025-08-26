#!/usr/bin/env python
"""
Script para demostrar las mejoras implementadas en AgroSoft
"""

import sys
import os
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosoft.settings')

import django
django.setup()

from productores.sipsa_service import SipsaService

def demostrar_fechas_funcionando():
    """
    Demuestra que las fechas ahora se muestran correctamente
    """
    print("📅 DEMOSTRACIÓN: FECHAS FUNCIONANDO")
    print("=" * 50)
    
    sipsa = SipsaService()
    fecha_test = datetime(2025, 6, 15)
    
    recomendaciones = sipsa.obtener_productos_recomendados("Facatativá", fecha_test, 18.5)
    
    print(f"Fecha de prueba: {fecha_test.strftime('%d/%m/%Y')}")
    print(f"Temperatura: 18.5°C")
    print("\nPrimeras 3 recomendaciones con fechas:")
    
    for i, rec in enumerate(recomendaciones[:3], 1):
        fecha_obj = rec['fecha_ultimo_precio']
        fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
        print(f"{i}. {rec['producto']}: Última actualización {fecha_formateada}")

def demostrar_factor_climatico():
    """
    Demuestra cómo el factor climático afecta las recomendaciones
    """
    print("\n\n🌡️ DEMOSTRACIÓN: FACTOR CLIMÁTICO")
    print("=" * 50)
    
    sipsa = SipsaService()
    municipio = "Madrid"
    fecha = datetime(2025, 4, 15)
    
    # Probar diferentes temperaturas
    temperaturas = [8, 15, 25, 30]
    
    for temp in temperaturas:
        print(f"\n🌡️ Temperatura: {temp}°C")
        print("-" * 25)
        
        recomendaciones = sipsa.obtener_productos_recomendados(municipio, fecha, temp)
        
        # Mostrar top 3 con factores climáticos
        for i, rec in enumerate(recomendaciones[:3], 1):
            factor_clima = rec['clima_factor']
            if factor_clima > 1.1:
                estado_clima = "🌡️ Ideal"
            elif factor_clima < 0.9:
                estado_clima = "❄️ Adverso"
            else:
                estado_clima = "🌤️ Adecuado"
            
            print(f"{i}. {rec['producto']}: {estado_clima} ({factor_clima:.2f}x)")

def demostrar_combinacion_factores():
    """
    Demuestra cómo todos los factores trabajan juntos
    """
    print("\n\n🎯 DEMOSTRACIÓN: COMBINACIÓN DE FACTORES")
    print("=" * 50)
    
    sipsa = SipsaService()
    
    # Escenario: Papa Criolla en diferentes contextos
    contextos = [
        ("Subachoque", datetime(2025, 1, 15), 12),  # Municipio favorable, época buena, clima ideal
        ("Mosquera", datetime(2025, 6, 15), 25),    # Municipio desfavorable, época mala, clima caliente
        ("Facatativá", datetime(2025, 3, 15), 15),  # Municipio bueno, época regular, clima perfecto
    ]
    
    print("Producto: PAPA CRIOLLA en diferentes contextos\n")
    
    for municipio, fecha, temp in contextos:
        recomendaciones = sipsa.obtener_productos_recomendados(municipio, fecha, temp)
        
        # Buscar Papa Criolla
        papa = next((r for r in recomendaciones if 'PAPA CRIOLLA' in r['producto']), None)
        
        if papa:
            print(f"📍 {municipio} - {fecha.strftime('%B')} - {temp}°C:")
            print(f"   💰 Precio: ${papa['precio_actual']}")
            print(f"   🏘️ Factor Municipal: {papa['municipio_factor']:.2f}x")
            print(f"   🌡️ Factor Climático: {papa['clima_factor']:.2f}x")
            print(f"   ⭐ Rentabilidad: {papa['rentabilidad_estimada']:.1f}%")
            print(f"   📊 Posición en ranking: {recomendaciones.index(papa) + 1}")
            print()

def demostrar_apis_disponibles():
    """
    Información sobre APIs que se investigaron
    """
    print("\n\n🔍 INVESTIGACIÓN DE APIS REALES")
    print("=" * 50)
    
    print("APIs Investigadas:")
    print("1. ✅ SIPSA-DANE: Existe pero estructura compleja")
    print("2. ❌ Corabastos Directo: No tiene API pública")
    print("3. ⚠️ datos.gov.co: Datos disponibles pero formato CSV")
    
    print("\nSolución Actual:")
    print("• 📊 Datos simulados basados en precios reales de mercado")
    print("• 🔄 Sistema preparado para integrar APIs reales")
    print("• 🎯 Factores realistas (municipal, estacional, climático)")
    print("• 📈 Algoritmos de recomendación funcionales")
    
    print("\nPróximos Pasos para APIs Reales:")
    print("• 🤝 Contactar directamente con Corabastos")
    print("• 📋 Solicitar acceso a datos históricos")
    print("• 🔌 Implementar scraping ético de boletines PDF")
    print("• 📊 Integrar con SIPSA cuando mejore documentación")

if __name__ == "__main__":
    try:
        print("🚀 DEMOSTRACIÓN DE MEJORAS EN AGROSOFT")
        print("=" * 60)
        
        demostrar_fechas_funcionando()
        demostrar_factor_climatico()
        demostrar_combinacion_factores()
        demostrar_apis_disponibles()
        
        print("\n\n✅ RESUMEN DE MEJORAS IMPLEMENTADAS:")
        print("1. 📅 Fechas de actualización ahora se muestran correctamente")
        print("2. 🌡️ Factor climático integrado usando API de OpenWeatherMap")
        print("3. 🎯 Sistema dinámico que responde a municipio + fecha + clima")
        print("4. 🔍 Investigación completa de APIs disponibles")
        print("5. 📊 Base sólida para integrar datos reales en el futuro")
        
        print("\n🌐 Prueba en el navegador:")
        print("• Cambia municipio, fecha y observa los cambios")
        print("• Nota las columnas de Factor Municipal y Climático")
        print("• Las fechas de actualización ahora aparecen")
        print("• El clima real afecta las recomendaciones")
        
    except Exception as e:
        print(f"💥 Error durante la demostración: {e}")
        sys.exit(1)
