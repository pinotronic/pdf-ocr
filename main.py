import tkinter as tk
from ui_interface import PDFOptimizerUI
import os
from config import Config
import requests

def main():
    # Verificar configuración según el modo
    if Config.USE_LOCAL_MODEL:
        print("🔧 Modo: LOCAL (Ollama)")
        print(f"📦 Modelo: {Config.OLLAMA_MODEL}")
        print(f"🌐 URL: {Config.OLLAMA_URL}")
        
        # Verificar que Ollama esté corriendo
        try:
            response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama está disponible")
            else:
                print("⚠️ Advertencia: Ollama responde pero con error")
        except:
            print("❌ Error: No se puede conectar a Ollama")
            print("   Por favor verifica que Ollama esté corriendo")
            print(f"   Intenta: ollama run {Config.OLLAMA_MODEL}")
            input("Presiona Enter para salir...")
            return
    else:
        print("🔧 Modo: API (DeepSeek Cloud)")
        if not Config.DEEPSEEK_API_KEY:
            print("❌ Error: No se encontró DEEPSEEK_API_KEY")
            print("Por favor crea un archivo .env con:")
            print("DEEPSEEK_API_KEY=tu_api_key_aqui")
            print("O activa el modo local con: USE_LOCAL_MODEL=true")
            input("Presiona Enter para salir...")
            return
        print("✅ API Key configurada")
    
    # Crear ventana principal
    root = tk.Tk()
    app = PDFOptimizerUI(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()