"""
Productos cultivados en la Sabana de Occidente - Colombia
Este archivo contiene la lista oficial de productos que se cultivan en la sabana de occidente
y que serán utilizados para las recomendaciones del sistema.
"""

# Lista oficial de productos cultivados en la Sabana de Occidente
PRODUCTOS_SABANA_OCCIDENTE = {
    # Papas
    'papa_sabanera': {'nombre': 'Papa Sabanera', 'categoria': 'tuberculo'},
    'papa_pastusa': {'nombre': 'Papa Pastusa', 'categoria': 'tuberculo'},
    'papa_suprema': {'nombre': 'Papa Suprema', 'categoria': 'tuberculo'},
    'papa_r12': {'nombre': 'Papa R12', 'categoria': 'tuberculo'},
    
    # Legumbres
    'arveja_verde_sabanera': {'nombre': 'Arveja Verde Sabanera', 'categoria': 'legumbre'},
    'haba_verde_sabanera': {'nombre': 'Haba Verde Sabanera', 'categoria': 'legumbre'},
    
    # Verduras
    'zanahoria': {'nombre': 'Zanahoria', 'categoria': 'verdura'},
    'cebolla_cabezona_blanca': {'nombre': 'Cebolla Cabezona Blanca', 'categoria': 'verdura'},
    'cebolla_cabezona_roja': {'nombre': 'Cebolla Cabezona Roja', 'categoria': 'verdura'},
    'cebolla_larga': {'nombre': 'Cebolla Larga', 'categoria': 'verdura'},
    'maíz_duro_blanco': {'nombre': 'Maíz Duro Blanco', 'categoria': 'cereal'},
    'maíz_duro_amarillo': {'nombre': 'Maíz Duro Amarillo', 'categoria': 'cereal'},
    
    # Hortalizas
    'repollo': {'nombre': 'Repollo', 'categoria': 'hortaliza'},
    'remolacha': {'nombre': 'Remolacha', 'categoria': 'hortaliza'},
    'habichuela': {'nombre': 'Habichuela', 'categoria': 'hortaliza'},
    'lechuga': {'nombre': 'Lechuga', 'categoria': 'hortaliza'},
    'espinaca': {'nombre': 'Espinaca', 'categoria': 'hortaliza'},
    'acelga': {'nombre': 'Acelga', 'categoria': 'hortaliza'},
    'brócoli': {'nombre': 'Brócoli', 'categoria': 'hortaliza'},
    'coliflor': {'nombre': 'Coliflor', 'categoria': 'hortaliza'},
}

# Diccionario de precios actualizados de Corabastos (2024)
PRECIOS_CORABASTOS_2024 = {
    'papa_sabanera': 3000,
    'papa_pastusa': 2800,
    'papa_suprema': 3200,
    'papa_r12': 2600,
    'arveja_verde_sabanera': 4500,
    'haba_verde_sabanera': 4200,
    'zanahoria': 2000,
    'cebolla_cabezona_blanca': 2400,
    'cebolla_cabezona_roja': 2200,
    'cebolla_larga': 2000,
    'maíz_duro_blanco': 2800,
    'maíz_duro_amarillo': 2600,
    'repollo': 1800,
    'remolacha': 1500,
    'habichuela': 3500,
    'lechuga': 1800,
    'espinaca': 5000,
    'acelga': 2000,
    'brócoli': 4200,
    'coliflor': 3800,
}

# Datos climáticos por cultivo para la Sabana de Occidente
CLIMA_POR_CULTIVO = {
    'papa_sabanera': {'meses_optimos': [1, 2, 3, 7, 8, 9, 10], 'temp_optima': '10-18°C', 'precipitacion': '600-800mm'},
    'papa_pastusa': {'meses_optimos': [1, 2, 3, 7, 8, 9, 10], 'temp_optima': '10-18°C', 'precipitacion': '600-800mm'},
    'papa_suprema': {'meses_optimos': [1, 2, 3, 7, 8, 9, 10], 'temp_optima': '10-18°C', 'precipitacion': '600-800mm'},
    'papa_r12': {'meses_optimos': [1, 2, 3, 7, 8, 9, 10], 'temp_optima': '10-18°C', 'precipitacion': '600-800mm'},
    'arveja_verde_sabanera': {'meses_optimos': [2, 3, 4, 5, 9, 10, 11], 'temp_optima': '15-25°C', 'precipitacion': '800-1200mm'},
    'haba_verde_sabanera': {'meses_optimos': [2, 3, 4, 5, 9, 10, 11], 'temp_optima': '15-25°C', 'precipitacion': '800-1200mm'},
    'zanahoria': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'cebolla_cabezona_blanca': {'meses_optimos': [3, 4, 5, 9, 10, 11], 'temp_optima': '15-25°C', 'precipitacion': '600-800mm'},
    'cebolla_cabezona_roja': {'meses_optimos': [3, 4, 5, 9, 10, 11], 'temp_optima': '15-25°C', 'precipitacion': '600-800mm'},
    'cebolla_larga': {'meses_optimos': [3, 4, 5, 9, 10, 11], 'temp_optima': '15-25°C', 'precipitacion': '600-800mm'},
    'maíz_duro_blanco': {'meses_optimos': [3, 4, 5, 9, 10, 11], 'temp_optima': '20-30°C', 'precipitacion': '600-800mm'},
    'maíz_duro_amarillo': {'meses_optimos': [3, 4, 5, 9, 10, 11], 'temp_optima': '20-30°C', 'precipitacion': '600-800mm'},
    'repollo': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'remolacha': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'habichuela': {'meses_optimos': [2, 3, 4, 5, 9, 10, 11], 'temp_optima': '18-25°C', 'precipitacion': '800-1000mm'},
    'lechuga': {'meses_optimos': [2, 3, 4, 5, 9, 10, 11], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'espinaca': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'acelga': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'brócoli': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
    'coliflor': {'meses_optimos': [2, 3, 4, 8, 9, 10], 'temp_optima': '15-20°C', 'precipitacion': '600-800mm'},
}

# Función para validar si un producto pertenece a la sabana de occidente
def es_producto_sabana_occidente(producto):
    """Verifica si un producto está en la lista de la sabana de occidente"""
    return producto.lower() in [p.lower() for p in PRODUCTOS_SABANA_OCCIDENTE.keys()]

# Función para obtener recomendaciones basadas en fecha y municipio
def obtener_recomendaciones_sabana_occidente(municipio, fecha_siembra):
    """Genera recomendaciones de cultivos basadas en municipio y fecha"""
    mes = fecha_siembra.month
    
    recomendaciones = []
    for producto, data in PRODUCTOS_SABANA_OCCIDENTE.items():
        if mes in CLIMA_POR_CULTIVO.get(producto, {}).get('meses_optimos', []):
            fecha_cosecha = fecha_siembra + timedelta(days=90)  # Ajustar según cultivo
            recomendaciones.append({
                'cultivo': data['nombre'],
                'fecha_cosecha': fecha_cosecha,
                'precio_kg': PRECIOS_CORABASTOS_2024.get(producto, 0),
                'meses_optimos': CLIMA_POR_CULTIVO.get(producto, {}).get('meses_optimos', []),
                'temp_optima': CLIMA_POR_CULTIVO.get(producto, {}).get('temp_optima', ''),
                'precipitacion': CLIMA_POR_CULTIVO.get(producto, {}).get('precipitacion', '')
            })
    
    return sorted(recomendaciones, key=lambda x: x['precio_kg'], reverse=True)[:3]
