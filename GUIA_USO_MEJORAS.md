#  Guía de Uso - Mejoras OCR

## Casos de Uso Comunes

### 1 Procesar un PDF Normal (uso estándar)

El sistema aplicará automáticamente:
-  Extracción a 300 DPI
-  Preprocesamiento de imágenes
-  Prompts optimizados
-  Detección mejorada de texto

### 2 Procesar PDF con Texto MUY Pequeño

Edita tu archivo .env:
ENHANCE_IMAGE_QUALITY=true
IMAGE_SCALE_FACTOR=2.0

### 3 Procesar PDF de Alta Calidad

Si tu PDF ya tiene buena calidad, desactiva el preprocesamiento:
ENHANCE_IMAGE_QUALITY=false

Consulta MEJORAS_OCR.md para documentación completa.
