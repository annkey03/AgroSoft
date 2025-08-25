# 🌱 AgroSoft - Sistema de Recomendaciones Agrícolas

**AgroSoft** es una aplicación web desarrollada en Django que ayuda a los productores de la Sabana Occidental de Cundinamarca a tomar decisiones informadas sobre qué cultivos sembrar, basándose en análisis de precios de mercado y tendencias.

## ✨ Características Principales

- 📊 **Análisis de Precios**: Datos basados en precios típicos de Corabastos
- 📈 **Tendencias de Mercado**: Análisis de subida, bajada o estabilidad de precios
- 🌍 **Información Climática**: Integración con OpenWeatherMap
- 🏘️ **Enfoque Regional**: Específico para municipios de la Sabana Occidental
- 💰 **Cálculo de Rentabilidad**: Estimaciones de rentabilidad por producto
- 🎯 **Recomendaciones Inteligentes**: Top 10 productos más prometedores

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd agrosoft
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Probar la conexión de datos**
   ```bash
   python test_sipsa.py
   ```

4. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

5. **Abrir en el navegador**
   - Ir a: `http://127.0.0.1:8000/`

## 🌐 Uso de la Aplicación

### Página Principal
1. **Seleccionar Municipio**: Elige entre Facatativá, Madrid, Mosquera, El Rosal, Subachoque, o Bojacá
2. **Fecha de Siembra**: Selecciona la fecha proyectada de siembra
3. **Obtener Recomendaciones**: Haz clic en el botón para generar el análisis

### Información Mostrada
- **Estadísticas del Mercado**: Total de productos, precios promedio, última actualización
- **Tabla de Recomendaciones**: 
  - Producto y precio actual
  - Precio promedio histórico
  - Tendencia (Subiendo/Bajando/Estable)
  - Presentación y unidad de medida
  - Rentabilidad estimada
  - Fecha de última actualización

## 📊 Productos Incluidos

La aplicación analiza 15 productos típicos de la Sabana Occidental:

- **Tubérculos**: Papa Criolla, Papa Pastusa
- **Hortalizas de Raíz**: Zanahoria, Remolacha
- **Aromáticas**: Cilantro, Perejil, Apio
- **Cebollas**: Cebolla Cabezona, Cebolla Larga
- **Hojas Verdes**: Lechuga, Acelga, Espinaca
- **Crucíferas**: Repollo, Brócoli, Coliflor

## 🔧 API Endpoints

### `/api/precios/`
Endpoint JSON para obtener datos de precios programáticamente.

**Parámetros opcionales:**
- `producto`: Filtrar por nombre de producto específico

**Ejemplo:**
```
GET /api/precios/?producto=PAPA
```

## 🌤️ Configuración Climática (Opcional)

Para obtener datos climáticos reales:

1. Registrarse en [OpenWeatherMap](https://openweathermap.org/api)
2. Obtener una API key gratuita
3. Configurar la variable de entorno:
   ```bash
   set OPENWEATHER_API_KEY=tu_api_key_aqui
   ```

## 📁 Estructura del Proyecto

```
agrosoft/
├── agrosoft/           # Configuración principal de Django
├── productores/        # Aplicación principal
│   ├── models.py      # Modelos de datos
│   ├── views.py       # Lógica de vistas
│   ├── sipsa_service.py # Servicio de datos de precios
│   └── admin.py       # Configuración del admin
├── templates/          # Plantillas HTML
├── requirements.txt    # Dependencias
├── test_sipsa.py      # Script de pruebas
└── README.md          # Este archivo
```

## 🎯 Casos de Uso

### Para Productores
- Decidir qué cultivos sembrar según rentabilidad
- Planificar siembras según tendencias de precios
- Comparar precios entre diferentes productos

### Para Asesores Técnicos
- Brindar recomendaciones basadas en datos
- Analizar tendencias del mercado regional
- Planificar estrategias de producción

### Para Cooperativas
- Orientar a asociados sobre cultivos rentables
- Planificar compras y ventas conjuntas
- Analizar oportunidades de mercado

## 🔄 Actualización de Datos

Los datos se generan con variaciones realistas basadas en:
- Precios históricos típicos de Corabastos
- Variaciones estacionales simuladas
- Fluctuaciones normales del mercado

## 🤝 Contribuciones

Para mejorar el proyecto:
1. Reportar bugs o sugerencias
2. Proponer nuevos productos para análisis
3. Mejorar algoritmos de recomendación
4. Agregar nuevas funcionalidades

## 📞 Soporte

Si encuentras problemas:
1. Verificar que todas las dependencias estén instaladas
2. Ejecutar `python test_sipsa.py` para diagnosticar
3. Revisar que el puerto 8000 esté disponible
4. Consultar los logs del servidor Django

## 📈 Próximas Mejoras

- Integración con APIs reales de precios
- Análisis de costos de producción
- Alertas de precios por email/SMS
- Gráficos interactivos de tendencias
- Exportación de reportes en PDF
- Aplicación móvil

---

**Desarrollado para apoyar a los productores de la Sabana Occidental de Cundinamarca** 🇨🇴
