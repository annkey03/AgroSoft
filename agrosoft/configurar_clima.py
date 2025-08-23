#!/usr/bin/env python
"""
Script para configurar y probar la API del clima
"""

import os
import requests
from datetime import datetime

def obtener_api_key_gratis():
    """
    Instrucciones para obtener API key gratuita
    """
    print("🌤️ CÓMO OBTENER API KEY GRATUITA DE OPENWEATHERMAP")
    print("=" * 60)
    print("1. Ve a: https://openweathermap.org/api")
    print("2. Haz clic en 'Sign Up' (registrarse)")
    print("3. Completa el formulario gratuito")
    print("4. Verifica tu email")
    print("5. Ve a 'API Keys' en tu dashboard")
    print("6. Copia tu API key")
    print("\n📝 LÍMITES GRATUITOS:")
    print("• 1,000 llamadas por día")
    print("• 60 llamadas por minuto")
    print("• Más que suficiente para AgroSoft")

def configurar_api_key():
    """
    Configurar la API key
    """
    print("\n⚙️ CONFIGURACIÓN DE API KEY")
    print("=" * 40)
    
    api_key = input("Ingresa tu API key de OpenWeatherMap: ").strip()
    
    if api_key:
        # Probar la API key
        print("🔍 Probando API key...")
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q=Facatativá,CO&appid={api_key}&units=metric&lang=es"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                descripcion = data['weather'][0]['description']
                
                print(f"✅ API key válida!")
                print(f"🌡️ Temperatura en Facatativá: {temp}°C")
                print(f"🌤️ Condiciones: {descripcion}")
                
                # Guardar en archivo de configuración
                with open('.env', 'w') as f:
                    f.write(f"OPENWEATHER_API_KEY={api_key}\n")
                
                print(f"\n💾 API key guardada en archivo .env")
                print("🔄 Reinicia el servidor Django para aplicar cambios")
                
                return api_key
                
            else:
                print(f"❌ Error: {response.status_code}")
                print("Verifica que la API key sea correcta")
                
        except Exception as e:
            print(f"💥 Error probando API: {e}")
    
    return None

def usar_clima_simulado():
    """
    Configurar clima simulado como alternativa
    """
    print("\n🎭 ALTERNATIVA: CLIMA SIMULADO")
    print("=" * 40)
    print("Si no quieres usar API real, puedo configurar clima simulado")
    print("que cambie según municipio y fecha.")
    
    usar_simulado = input("¿Usar clima simulado? (s/n): ").lower().strip()
    
    if usar_simulado == 's':
        return True
    
    return False

if __name__ == "__main__":
    print("🌡️ CONFIGURADOR DE CLIMA PARA AGROSOFT")
    print("=" * 50)
    
    print("Opciones:")
    print("1. Configurar API real de OpenWeatherMap (recomendado)")
    print("2. Usar clima simulado")
    
    opcion = input("\nElige opción (1 o 2): ").strip()
    
    if opcion == "1":
        obtener_api_key_gratis()
        api_key = configurar_api_key()
        
        if not api_key:
            print("\n🔄 Configurando clima simulado como fallback...")
            usar_clima_simulado()
    
    elif opcion == "2":
        if usar_clima_simulado():
            print("✅ Clima simulado configurado")
    
    else:
        print("❌ Opción no válida")
