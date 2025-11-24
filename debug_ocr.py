"""
Script de diagnóstico para verificar qué se envía a Ollama y qué responde
"""
import requests
import base64
import json
from config import Config
from PIL import Image
import io

def test_ollama_with_image():
    """Prueba OCR con una imagen de prueba"""
    print("=" * 70)
    print("DIAGNÓSTICO DE OCR CON OLLAMA")
    print("=" * 70)
    print()
    
    # Información de configuración
    print(f"📋 Configuración:")
    print(f"   Modelo: {Config.OLLAMA_MODEL}")
    print(f"   URL: {Config.OLLAMA_URL}")
    print()
    
    # Crear una imagen de prueba simple con texto
    print("🖼️ Creando imagen de prueba con texto...")
    img = Image.new('RGB', (400, 200), color='white')
    
    # Guardar como PNG
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
    
    print(f"   Tamaño de imagen base64: {len(base64_image)} caracteres")
    print()
    
    # Probar con el modelo
    print("🔄 Enviando solicitud a Ollama...")
    print()
    
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": "Describe lo que ves en esta imagen. Si hay texto, extráelo.",
        "images": [base64_image],
        "stream": False
    }
    
    print(f"📤 Payload enviado:")
    print(f"   - Model: {payload['model']}")
    print(f"   - Prompt: {payload['prompt'][:50]}...")
    print(f"   - Images: 1 imagen en base64")
    print(f"   - Stream: {payload['stream']}")
    print()
    
    try:
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=120
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Respuesta JSON completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print()
            
            extracted_text = result.get('response', '')
            
            if extracted_text:
                print("✅ TEXTO EXTRAÍDO:")
                print(f"   {extracted_text}")
                print()
                print(f"   Longitud: {len(extracted_text)} caracteres")
            else:
                print("❌ NO SE EXTRAJO TEXTO")
                print("   La clave 'response' está vacía o no existe")
                print()
                print("   Claves disponibles en la respuesta:")
                for key in result.keys():
                    print(f"      - {key}: {result[key]}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   {response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: El modelo tardó más de 120 segundos")
        print("   Esto puede indicar que:")
        print("   1. El modelo es muy grande y está cargando")
        print("   2. El modelo no está optimizado para OCR")
        print("   3. Hay un problema con el formato de la imagen")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()
    print("=" * 70)

def test_model_capabilities():
    """Prueba si el modelo soporta visión"""
    print()
    print("=" * 70)
    print("VERIFICACIÓN DE CAPACIDADES DEL MODELO")
    print("=" * 70)
    print()
    
    try:
        # Obtener información del modelo
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/show",
            json={"name": Config.OLLAMA_MODEL},
            timeout=10
        )
        
        if response.status_code == 200:
            model_info = response.json()
            print("📦 Información del modelo:")
            print(json.dumps(model_info, indent=2, ensure_ascii=False))
        else:
            print(f"⚠️ No se pudo obtener info del modelo: {response.status_code}")
    
    except Exception as e:
        print(f"⚠️ Error al obtener info: {str(e)}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_ollama_with_image()
    test_model_capabilities()
    print()
    input("Presiona Enter para salir...")
