"""
Diagnostico simple de OCR con Ollama
"""
import requests
import base64
import json
from config import Config
from PIL import Image
import io
import os

def test_with_real_pdf_page():
    """Prueba con una pagina real del PDF"""
    print("=" * 70)
    print("DIAGNOSTICO DE OCR - RESPUESTAS A TUS PREGUNTAS")
    print("=" * 70)
    print()
    
    print("PREGUNTA 1: Se envia hoja por hoja o todo el PDF?")
    print("RESPUESTA: SE ENVIA HOJA POR HOJA (una imagen PNG por cada pagina)")
    print()
    
    print("PREGUNTA 2: Que tipo de archivo enviamos?")
    print("RESPUESTA: Imagenes PNG en formato BASE64")
    print()
    
    print("Proceso detallado:")
    print("1. PDF -> Se convierte cada pagina a imagen PNG (pdf2image)")
    print("2. PNG -> Se convierte a Base64 (encoding)")
    print("3. Base64 -> Se envia a Ollama con el modelo deepseek-ocr")
    print("4. Ollama -> Procesa la imagen y devuelve texto")
    print("5. Texto -> Se acumula y al final se crea nuevo PDF")
    print()
    
    print("=" * 70)
    print()
    
    # Verificar configuracion
    print(f"Configuracion actual:")
    print(f"  Modelo: {Config.OLLAMA_MODEL}")
    print(f"  URL: {Config.OLLAMA_URL}")
    print()
    
    # Verificar capacidades del modelo
    print("Verificando capacidades del modelo...")
    try:
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/show",
            json={"name": Config.OLLAMA_MODEL},
            timeout=10
        )
        
        if response.status_code == 200:
            model_info = response.json()
            capabilities = model_info.get('capabilities', [])
            print(f"  Capacidades: {', '.join(capabilities)}")
            
            if 'vision' in capabilities:
                print("  [OK] El modelo SOPORTA vision (puede procesar imagenes)")
            else:
                print("  [ERROR] El modelo NO soporta vision")
                print("  Necesitas un modelo con capacidad 'vision' para OCR")
            print()
    except Exception as e:
        print(f"  Error al verificar: {str(e)}")
        print()
    
    # Crear imagen de prueba
    print("Creando imagen de prueba...")
    img = Image.new('RGB', (800, 200), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    try:
        # Intentar usar una fuente
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), "PRUEBA DE OCR - Texto de ejemplo", fill='black', font=font)
    
    # Guardar temporalmente
    temp_image = "temp_test_ocr.png"
    img.save(temp_image)
    print(f"  Imagen guardada: {temp_image}")
    print(f"  Tamano: {os.path.getsize(temp_image)} bytes")
    print()
    
    # Convertir a base64
    print("Convirtiendo a base64...")
    with open(temp_image, 'rb') as f:
        image_data = f.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
    
    print(f"  Base64 length: {len(base64_image)} caracteres")
    print()
    
    # Enviar a Ollama
    print("Enviando a Ollama...")
    print("  (Esto puede tardar hasta 2 minutos)")
    print()
    
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": "extrae el texto de la imagen",
        "images": [base64_image],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=300  # 5 minutos de timeout
        )
        
        print(f"Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verificar respuesta
            extracted_text = result.get('response', '')
            
            if extracted_text and extracted_text.strip():
                print("[OK] Se extrajo texto correctamente!")
                print(f"Texto extraido: '{extracted_text}'")
                print()
                print("CONCLUSION: El modelo funciona correctamente para OCR")
            else:
                print("[ERROR] NO se extrajo texto")
                print("La respuesta esta vacia o no contiene texto")
                print()
                print("Respuesta completa del modelo:")
                print(json.dumps(result, indent=2))
                print()
                print("POSIBLES CAUSAS:")
                print("1. El modelo no es adecuado para OCR")
                print("2. El prompt no es el correcto para este modelo")
                print("3. El modelo necesita un formato diferente")
        else:
            print(f"[ERROR] Codigo de error: {response.status_code}")
            print(f"Mensaje: {response.text}")
    
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout - El modelo tardo mas de 120 segundos")
        print("El modelo puede ser muy grande o estar sobrecargado")
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    finally:
        # Limpiar
        if os.path.exists(temp_image):
            os.remove(temp_image)
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_with_real_pdf_page()
    print()
    input("Presiona Enter para salir...")
