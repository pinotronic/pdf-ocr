import requests
import base64
from config import Config

def test_deepseek_api():
    """Prueba simple de la API de DeepSeek"""
    print("🧪 Probando API de DeepSeek...")
    
    # Verificar API key
    if not Config.DEEPSEEK_API_KEY:
        print("❌ No hay API Key configurada")
        return False
    
    # Crear una imagen de prueba simple (puedes usar cualquier imagen)
    try:
        # Headers
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Payload de prueba simple (solo texto)
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": "Responde con 'OK' si la API funciona correctamente"
                }
            ],
            "max_tokens": 100
        }
        
        print("🔍 Enviando solicitud de prueba...")
        response = requests.post(
            "https://api.deepseek.com/chat/completions", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        print(f"📡 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API funciona: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Error en API: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()