"""
Script simple para probar el traductor
"""
from deepseek_client import TranslationClient
from config import Config

print(f"Modelo de traducción: {Config.TRANSLATION_MODEL}")
print(f"URL Ollama: {Config.OLLAMA_URL}")
print()

# Crear cliente de traducción
translator = TranslationClient()

# Texto de prueba en inglés
test_text = """
INVOICE

Date: November 24, 2025
Invoice Number: INV-2025-001

Product: Professional Services
Amount: $1,500.00

Thank you for your business.
"""

print("Texto original:")
print(test_text)
print()
print("=" * 70)
print()

print("Traduciendo...")
translated = translator.translate_to_spanish(test_text, page_num=1)

print()
print("Texto traducido:")
print(translated)
print()

if translated == test_text:
    print("⚠️ ADVERTENCIA: El texto no cambió, puede que no se haya traducido")
else:
    print("✓ Traducción exitosa!")

input("\nPresiona Enter para salir...")
