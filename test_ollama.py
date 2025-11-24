"""
Script de prueba para verificar la conexión con Ollama y el modelo DeepSeek
"""
import requests
import json
from config import Config

def test_ollama_connection():
    """Prueba la conexión con Ollama"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN CON OLLAMA")
    print("=" * 60)
    print()
    
    # Verificar configuración
    print(f"📋 Configuración:")
    print(f"   URL: {Config.OLLAMA_URL}")
    print(f"   Modelo: {Config.OLLAMA_MODEL}")
    print(f"   Modo Local: {Config.USE_LOCAL_MODEL}")
    print()
    
    # Probar conexión
    print("🔄 Probando conexión con Ollama...")
    try:
        response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está corriendo y responde correctamente")
            print()
            
            # Listar modelos disponibles
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"📦 Modelos instalados ({len(models)}):")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    size_gb = size / (1024 ** 3)
                    print(f"   • {name} ({size_gb:.2f} GB)")
                print()
                
                # Verificar si el modelo configurado está disponible
                model_names = [m.get('name', '') for m in models]
                if any(Config.OLLAMA_MODEL in name for name in model_names):
                    print(f"✅ Modelo '{Config.OLLAMA_MODEL}' encontrado")
                else:
                    print(f"❌ Modelo '{Config.OLLAMA_MODEL}' NO encontrado")
                    print(f"   Para instalarlo ejecuta: ollama pull {Config.OLLAMA_MODEL}")
            else:
                print("⚠️ No hay modelos instalados en Ollama")
                print(f"   Para instalar ejecuta: ollama pull {Config.OLLAMA_MODEL}")
        else:
            print(f"❌ Error: Ollama respondió con código {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a Ollama")
        print("   Verifica que Ollama esté corriendo")
        print("   Puedes iniciarlo con: ollama serve")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("=" * 60)

def test_simple_prompt():
    """Prueba un prompt simple con el modelo"""
    print()
    print("=" * 60)
    print("PRUEBA DE GENERACIÓN DE TEXTO")
    print("=" * 60)
    print()
    
    try:
        print("🔄 Enviando prompt de prueba al modelo...")
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": "Di 'Hola, funciono correctamente!' en español",
            "stream": False
        }
        
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '')
            print("✅ Respuesta del modelo:")
            print(f"   {text}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_ollama_connection()
    
    # Solo probar generación si la conexión fue exitosa
    try:
        response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            test_simple_prompt()
    except:
        pass
    
    print()
    input("Presiona Enter para salir...")
