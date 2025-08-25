#!/usr/bin/env python
"""
Script para investigar la estructura de datos de la API SIPSA
"""

import requests
import json

def investigar_api_sipsa():
    """
    Investiga la estructura de la API SIPSA
    """
    url = "https://www.datos.gov.co/api/views/ynsj-msaq/rows.json"
    
    try:
        print("🔍 Investigando estructura de la API SIPSA...")
        
        # Hacer petición con límite pequeño
        params = {'$limit': 5}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ Respuesta recibida. Status: {response.status_code}")
        print(f"📊 Claves principales: {list(data.keys())}")
        
        # Mostrar metadatos si existen
        if 'meta' in data:
            print("\n📋 Metadatos:")
            meta = data['meta']
            if 'view' in meta and 'columns' in meta['view']:
                print("🏷️ Columnas disponibles:")
                for i, col in enumerate(meta['view']['columns']):
                    print(f"  {i}: {col.get('name', 'Sin nombre')} - {col.get('fieldName', 'Sin campo')}")
        
        # Mostrar algunos datos de ejemplo
        if 'data' in data:
            print(f"\n📈 Total de registros en respuesta: {len(data['data'])}")
            print("\n🔍 Primeros 3 registros:")
            for i, row in enumerate(data['data'][:3]):
                print(f"  Registro {i+1}: {row}")
                print(f"    Longitud: {len(row)} campos")
        
        # Guardar respuesta completa para análisis
        with open('sipsa_debug.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n💾 Datos guardados en 'sipsa_debug.json' para análisis detallado")
        
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

if __name__ == "__main__":
    investigar_api_sipsa()
