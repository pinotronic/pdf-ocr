# Optimizador de PDF con DeepSeek OCR

Aplicación de escritorio para extraer y optimizar texto de archivos PDF usando OCR con inteligencia artificial.

## 🚀 Características

- **Dos modos de operación**:
  - 🏠 **Modo Local**: Usa Ollama con modelos DeepSeek instalados localmente (sin costos, privacidad total)
  - ☁️ **Modo API**: Usa la API de DeepSeek en la nube (requiere API key)
- Extracción de texto inteligente (texto nativo o OCR)
- Interfaz gráfica intuitiva
- Barra de progreso en tiempo real
- Optimización automática del PDF resultante

## 📋 Requisitos Previos

### Para Modo Local (Recomendado)
1. **Ollama** instalado en tu sistema
   - Windows: Descarga desde https://ollama.ai/download
   - Verifica la instalación: `ollama --version`

2. **Modelo DeepSeek** descargado
   ```bash
   ollama pull deepseek-r1:1.5b
   ```
   
   Modelos disponibles:
   - `deepseek-r1:1.5b` - Rápido, requiere ~1GB RAM (Recomendado para inicio)
   - `deepseek-r1:7b` - Balanceado, requiere ~4GB RAM
   - `deepseek-r1:14b` - Mejor precisión, requiere ~8GB RAM

### Para Modo API
- API Key de DeepSeek (obtener en https://platform.deepseek.com)

## 🔧 Instalación

1. **Clonar o descargar el repositorio**

2. **Instalar dependencias de Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar el archivo .env**
   
   Copia el archivo de ejemplo:
   ```bash
   copy .env.example .env
   ```
   
   Edita `.env` según tu modo preferido:
   
   **Para modo LOCAL (Ollama):**
   ```env
   USE_LOCAL_MODEL=true
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=deepseek-r1:1.5b
   ```
   
   **Para modo API:**
   ```env
   USE_LOCAL_MODEL=false
   DEEPSEEK_API_KEY=tu_api_key_aqui
   ```

4. **Verificar instalación**
   ```bash
   python test_ollama.py
   ```

## 🎯 Uso

### Iniciar la aplicación
```bash
python main.py
```

### Pasos para optimizar un PDF:
1. Haz clic en **"Examinar"** y selecciona tu archivo PDF
2. Haz clic en **"Optimizar PDF"**
3. Espera a que el procesamiento termine
4. El archivo optimizado se guardará con el sufijo `_optimizado.pdf`

## 🧪 Pruebas

### Probar conexión con Ollama
```bash
python test_ollama.py
```

### Probar extracción de texto (si existe test_api.py)
```bash
python test_api.py
```

## 📁 Estructura del Proyecto

```
pdfDeepsek/
├── main.py                 # Punto de entrada
├── config.py              # Configuración
├── deepseek_client.py     # Cliente DeepSeek (API y Local)
├── pdf_processor.py       # Procesamiento de PDFs
├── ui_interface.py        # Interfaz gráfica
├── test_ollama.py         # Prueba de Ollama
├── requirements.txt       # Dependencias Python
├── .env                   # Configuración local (no subir a git)
└── .env.example          # Plantilla de configuración
```

## ⚙️ Configuración Avanzada

### Cambiar modelo de Ollama

En `.env`, modifica:
```env
OLLAMA_MODEL=deepseek-r1:7b
```

Luego descarga el modelo:
```bash
ollama pull deepseek-r1:7b
```

### Cambiar URL de Ollama (si usas servidor remoto)

```env
OLLAMA_URL=http://tu-servidor:11434
```

### Alternar entre modo Local y API

Simplemente cambia en `.env`:
```env
USE_LOCAL_MODEL=true   # o false
```

## 🐛 Solución de Problemas

### Error: "No se puede conectar a Ollama"
- Verifica que Ollama esté corriendo: `ollama serve`
- Verifica el puerto: por defecto es 11434
- En Windows, Ollama se inicia automáticamente como servicio

### Error: "Modelo no encontrado"
- Lista modelos instalados: `ollama list`
- Instala el modelo: `ollama pull deepseek-r1:1.5b`
- Verifica el nombre en `.env` coincida con el instalado

### Error: "API Key no configurada"
- Si usas modo API, verifica que `DEEPSEEK_API_KEY` esté en `.env`
- Si usas modo local, asegúrate que `USE_LOCAL_MODEL=true`

### PDF no se procesa correctamente
- Verifica que poppler esté instalado (carpeta `poppler/` en el proyecto)
- Verifica que el PDF no esté protegido o encriptado
- Revisa los logs en la interfaz

## 🔐 Privacidad y Seguridad

- **Modo Local**: Todo el procesamiento ocurre en tu máquina, ningún dato sale de tu computadora
- **Modo API**: Los datos se envían a los servidores de DeepSeek para procesamiento

## 📝 Notas

- El primer uso del modelo puede tardar mientras se carga en memoria
- PDFs grandes pueden requerir varios minutos de procesamiento
- Se recomienda modo local para documentos sensibles

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un issue primero para discutir cambios mayores.

## 📄 Licencia

[Especifica tu licencia aquí]

## 👨‍💻 Autor

Pino Vargas
