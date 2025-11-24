"""
Script rápido para verificar que el modelo deepseek-r1 esté disponible
"""
import subprocess
import sys

def check_ollama_model():
    print("🔍 Verificando instalación de Ollama y modelo deepseek-r1...")
    print()
    
    try:
        # Verificar si Ollama está instalado
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Ollama está instalado")
            print()
            print("📦 Modelos disponibles:")
            print(result.stdout)
            
            # Verificar si deepseek-r1 está instalado
            if "deepseek-r1" in result.stdout.lower():
                print("✅ Modelo deepseek-r1 encontrado!")
                print()
                print("🎉 Todo listo para usar el modelo local!")
                print("   Ejecuta: python main.py")
            else:
                print("❌ Modelo deepseek-r1 NO encontrado")
                print()
                print("📥 Para instalarlo ejecuta uno de estos comandos:")
                print("   ollama pull deepseek-r1:1.5b   (Rápido, ~1GB)")
                print("   ollama pull deepseek-r1:7b     (Balanceado, ~4GB)")
                print("   ollama pull deepseek-r1:14b    (Mejor, ~8GB)")
        else:
            print("❌ Error al ejecutar Ollama")
            print(result.stderr)
    
    except FileNotFoundError:
        print("❌ Ollama no está instalado")
        print()
        print("📥 Descárgalo desde: https://ollama.ai/download")
        print("   Después ejecuta: ollama pull deepseek-r1:1.5b")
    
    except subprocess.TimeoutExpired:
        print("❌ Timeout al ejecutar Ollama")
        print("   Verifica que Ollama esté corriendo")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    check_ollama_model()
