# 🔌 Guía para Integrar APIs Reales de Precios Agrícolas

## 📊 Estado Actual vs Objetivo

### **Estado Actual** ✅
- Sistema funcional con datos simulados realistas
- Factores dinámicos (municipal, estacional, climático)
- Interfaz completa y responsive
- Base de código preparada para APIs reales

### **Objetivo** 🎯
- Datos reales de Corabastos y otros mercados mayoristas
- Actualización automática de precios
- Históricos reales para mejores predicciones

## 🔍 APIs Investigadas

### **1. SIPSA-DANE (Sistema de Información de Precios del Sector Agropecuario)**

**Estado**: ⚠️ Disponible pero complejo

**URL**: `https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa`

**Pros**:
- Datos oficiales del gobierno
- Incluye precios de Corabastos
- Actualización semanal

**Contras**:
- Documentación limitada
- Estructura de datos compleja
- No hay API REST clara

**Próximos pasos**:
```python
# Ejemplo de implementación futura
def obtener_datos_sipsa_real():
    # URL encontrada: https://www.datos.gov.co/api/views/[ID]/rows.json
    # Necesita investigación adicional del ID correcto
    pass
```

### **2. Corabastos Directo**

**Estado**: ❌ No disponible públicamente

**Investigación**:
- Sitio web: `https://corabastos.com.co/`
- No tiene API pública documentada
- Posible acceso mediante solicitud formal

**Recomendación**:
- Contactar directamente con Corabastos
- Solicitar acceso a datos históricos
- Proponer colaboración académica/investigativa

### **3. Datos Abiertos Colombia**

**Estado**: ⚠️ Datos disponibles en CSV

**URL**: `https://www.datos.gov.co/`

**Implementación posible**:
```python
def obtener_csv_datos_abiertos():
    # Descargar CSV periódicamente
    # Procesar y almacenar en base de datos local
    # Servir desde cache local
    pass
```

## 🛠️ Estrategias de Implementación

### **Estrategia 1: Scraping Ético de Boletines PDF**

```python
class BoletinScraper:
    """
    Extrae datos de boletines PDF de precios
    """
    def __init__(self):
        self.base_url = "URL_DE_BOLETINES"
    
    def descargar_boletin_reciente(self):
        # Descargar PDF más reciente
        pass
    
    def extraer_precios(self, pdf_path):
        # Usar PyMuPDF para extraer datos
        # Mejorar regex existente
        pass
```

### **Estrategia 2: API Híbrida**

```python
class HybridPriceService:
    """
    Combina múltiples fuentes de datos
    """
    def __init__(self):
        self.sources = [
            SipsaService(),
            BoletinScraper(),
            LocalCacheService()
        ]
    
    def obtener_precios_consolidados(self):
        # Intentar cada fuente en orden de prioridad
        # Fallback a datos simulados si falla todo
        pass
```

### **Estrategia 3: Base de Datos Local con Actualización Periódica**

```python
# models.py
class PrecioReal(models.Model):
    producto = models.CharField(max_length=100)
    precio_mayorista = models.DecimalField(max_digits=10, decimal_places=2)
    precio_minorista = models.DecimalField(max_digits=10, decimal_places=2)
    mercado = models.CharField(max_length=50)
    fecha = models.DateField()
    fuente = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ['producto', 'mercado', 'fecha']

# Tarea programada (Celery/Cron)
def actualizar_precios_diario():
    # Ejecutar cada día a las 6 AM
    # Obtener datos de todas las fuentes disponibles
    # Actualizar base de datos local
    pass
```

## 📞 Plan de Contacto con Corabastos

### **Carta de Solicitud de Datos**

```
Asunto: Solicitud de Colaboración - Proyecto AgroSoft para Productores de la Sabana Occidental

Estimados señores de Corabastos,

Somos desarrolladores de AgroSoft, una aplicación web que ayuda a productores agrícolas 
de la Sabana Occidental de Cundinamarca a tomar decisiones informadas sobre cultivos 
basándose en análisis de precios de mercado.

Solicitamos respetuosamente:

1. Acceso a datos históricos de precios mayoristas
2. Posibilidad de obtener actualizaciones periódicas
3. Colaboración en formato de datos (JSON/CSV/API)

Beneficios para Corabastos:
- Mayor visibilidad de sus datos de precios
- Apoyo a pequeños productores regionales
- Reconocimiento como fuente oficial de datos

Contacto: [tu_email@ejemplo.com]
Proyecto: https://github.com/tu-usuario/agrosoft
```

### **Información de Contacto**
- **Dirección**: AV CARRERA 80 No. 2 - 51, BOGOTÁ D.C.
- **Email**: info@corabastos.com.co
- **Teléfono**: Consultar en sitio web

## 🔄 Implementación Gradual

### **Fase 1: Preparación** (Actual ✅)
- [x] Sistema base funcionando
- [x] Estructura preparada para APIs
- [x] Interfaz completa

### **Fase 2: Datos Semi-Reales** (Próximo paso)
- [ ] Scraping de boletines PDF
- [ ] Base de datos local
- [ ] Actualización manual periódica

### **Fase 3: APIs Reales** (Objetivo final)
- [ ] Integración con SIPSA
- [ ] Acceso directo a Corabastos
- [ ] Actualización automática

### **Fase 4: Expansión** (Futuro)
- [ ] Más mercados mayoristas
- [ ] Predicciones con ML
- [ ] Alertas en tiempo real

## 💻 Código de Ejemplo para Integración

### **Servicio Híbrido**

```python
class RealDataService(SipsaService):
    """
    Extiende el servicio actual para usar datos reales cuando estén disponibles
    """
    
    def __init__(self):
        super().__init__()
        self.use_real_data = self._check_real_data_available()
    
    def _check_real_data_available(self):
        # Verificar si hay conexión a APIs reales
        try:
            # Intentar conexión a SIPSA
            response = requests.get(SIPSA_API_URL, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def obtener_precios_actuales(self, limit=1000):
        if self.use_real_data:
            return self._obtener_precios_reales(limit)
        else:
            return super().obtener_precios_actuales(limit)
    
    def _obtener_precios_reales(self, limit):
        # Implementar cuando tengamos acceso a APIs reales
        pass
```

## 📈 Métricas de Éxito

### **Indicadores de Calidad de Datos**
- Precisión vs precios reales de mercado
- Frecuencia de actualización
- Cobertura de productos

### **Indicadores de Uso**
- Número de consultas diarias
- Municipios más consultados
- Productos más buscados

## 🎯 Conclusión

El sistema actual de AgroSoft está **completamente preparado** para integrar APIs reales. Los datos simulados proporcionan una base sólida mientras se obtiene acceso a fuentes oficiales.

**Próximos pasos inmediatos**:
1. Contactar Corabastos formalmente
2. Investigar más a fondo la API de SIPSA
3. Implementar scraping de boletines como solución intermedia
4. Crear base de datos local para cache de datos reales

El proyecto tiene una arquitectura sólida que permite esta transición sin afectar la funcionalidad actual.
