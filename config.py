import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración API DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # Configuración Ollama (local)
    USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2-vision:latest")
    # Modelos recomendados para OCR:
    # - llama3.2-vision:latest (mejor para OCR)
    # - deepseek-r1:8b (alternativa con visión)
    # - deepseek-ocr:latest (específico pero puede necesitar prompt especial)
    
    # Configuración para traducción
    TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "llama3.2:latest")
    AUTO_TRANSLATE = os.getenv("AUTO_TRANSLATE", "false").lower() == "true"
    
    # Configuración general
    SUPPORTED_FORMATS = ['.pdf', '.PDF']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB