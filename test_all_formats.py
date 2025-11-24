"""
Prueba diferentes formatos de llamada a Ollama para deepseek-ocr
"""
import requests
import base64
import json
from config import Config
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Crea imagen de prueba con texto claro"""
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 150), "TEXTO DE PRUEBA", fill='black', font=font)
    
    # Guardar como PNG
    img.save("test_image.png")
    
    # Guardar como JPG
    img.save("test_image.jpg", quality=95)
    
    return "test_image.png", "test_image.jpg"

def test_format_1_png(image_path):
    """Formato 1: PNG con prompt simple"""
    print("\n" + "="*70)
    print("FORMATO 1: PNG + Prompt: 'extrae el texto de la imagen'")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
    
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
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            print(f"Status: OK")
            print(f"Texto: '{text}'")
            print(f"Longitud: {len(text)} caracteres")
            if text:
                print("✓ FUNCIONA!")
                return True
            else:
                print("✗ Respuesta vacia")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    return False

def test_format_2_jpg(image_path):
    """Formato 2: JPG con prompt simple"""
    print("\n" + "="*70)
    print("FORMATO 2: JPG + Prompt: 'extrae el texto de la imagen'")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
    
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
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            print(f"Status: OK")
            print(f"Texto: '{text}'")
            print(f"Longitud: {len(text)} caracteres")
            if text:
                print("✓ FUNCIONA!")
                return True
            else:
                print("✗ Respuesta vacia")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    return False

def test_format_3_chat(image_path):
    """Formato 3: Usando API de chat"""
    print("\n" + "="*70)
    print("FORMATO 3: API Chat con vision")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        "model": Config.OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "extrae el texto de la imagen",
                "images": [base64_image]
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/chat",
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('message', {}).get('content', '').strip()
            print(f"Status: OK")
            print(f"Texto: '{text}'")
            print(f"Longitud: {len(text)} caracteres")
            if text:
                print("✓ FUNCIONA!")
                return True
            else:
                print("✗ Respuesta vacia")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    return False

def test_format_4_simple_prompt(image_path):
    """Formato 4: Prompt minimalista"""
    print("\n" + "="*70)
    print("FORMATO 4: Prompt minimalista 'OCR'")
    print("="*70)
    
    with open(image_path, 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": "OCR",
        "images": [base64_image],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            print(f"Status: OK")
            print(f"Texto: '{text}'")
            print(f"Longitud: {len(text)} caracteres")
            if text:
                print("✓ FUNCIONA!")
                return True
            else:
                print("✗ Respuesta vacia")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("Creando imagenes de prueba...")
    png_path, jpg_path = create_test_image()
    print(f"  PNG: {png_path}")
    print(f"  JPG: {jpg_path}")
    
    # Probar diferentes formatos
    results = []
    results.append(("Formato 1 (PNG)", test_format_1_png(png_path)))
    results.append(("Formato 2 (JPG)", test_format_2_jpg(jpg_path)))
    results.append(("Formato 3 (Chat API)", test_format_3_chat(png_path)))
    results.append(("Formato 4 (Simple)", test_format_4_simple_prompt(png_path)))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    for name, success in results:
        status = "✓ FUNCIONA" if success else "✗ FALLO"
        print(f"{name}: {status}")
    
    print("\n")
    input("Presiona Enter para salir...")
