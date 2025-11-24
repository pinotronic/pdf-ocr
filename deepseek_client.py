import requests
import base64
import time
from config import Config

class DeepSeekClient:
    def __init__(self):
        self.use_local = Config.USE_LOCAL_MODEL
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.ollama_url = Config.OLLAMA_URL
        self.ollama_model = Config.OLLAMA_MODEL
        
        # Verificar configuración
        if self.use_local:
            self._verify_ollama_connection()
        elif not self.api_key:
            raise Exception("API Key de DeepSeek no configurada y modo local desactivado")
    
    def _verify_ollama_connection(self):
        """Verifica que Ollama esté disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                if not any(self.ollama_model in name for name in model_names):
                    print(f"⚠️ Advertencia: Modelo '{self.ollama_model}' no encontrado en Ollama")
                    print(f"   Modelos disponibles: {', '.join(model_names)}")
        except Exception as e:
            raise Exception(f"No se puede conectar a Ollama en {self.ollama_url}: {str(e)}")
    
    def extract_text_from_image(self, image_path):
        """Extrae texto de imagen usando DeepSeek OCR (local o API)"""
        if self.use_local:
            return self._extract_with_ollama(image_path)
        else:
            return self._extract_with_api(image_path)
    
    def _extract_with_ollama(self, image_path):
        """Extrae texto usando modelo local de Ollama"""
        try:
            # Convertir imagen a base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prompt simple y efectivo (probado por el usuario - funciona!)
            prompt = "extrae el texto de la imagen"
            
            # Payload para Ollama (configuración probada y funcional)
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            }
            
            print(f"[DEBUG] Enviando imagen a {self.ollama_model}... (tiempo estimado: 2 minutos)")
            
            # Llamada a Ollama (cada página tarda ~2 minutos según pruebas)
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=600  # 10 minutos de timeout por página para documentos complejos
            )
            
            if response.status_code != 200:
                raise Exception(f"Error {response.status_code} en Ollama: {response.text}")
            
            result = response.json()
            extracted_text = result.get('response', '').strip()
            
            print(f"[DEBUG] Respuesta recibida: {len(extracted_text)} caracteres")
            
            # Si la respuesta está vacía, intentar con contexto
            if not extracted_text:
                context = result.get('context', [])
                print(f"[DEBUG] Respuesta vacía. Context tokens: {len(context)}")
                
                # Verificar si hay un done_reason
                done_reason = result.get('done_reason', 'unknown')
                print(f"[DEBUG] Done reason: {done_reason}")
                
                raise Exception(f"Ollama devolvió respuesta vacía (done_reason: {done_reason}). Verifica que la imagen contenga texto legible.")
            
            return extracted_text
            
        except requests.exceptions.Timeout:
            raise Exception("Timeout: Ollama tardó demasiado en responder")
        except Exception as e:
            raise Exception(f"Error en OCR Ollama: {str(e)}")
    
    def _extract_with_api(self, image_path):
        """Extrae texto usando API de DeepSeek"""
        try:
            if not self.api_key or self.api_key == "":
                raise Exception("API Key de DeepSeek no configurada")
            
            # Convertir imagen a base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Extrae TODO el texto de esta imagen de manera precisa y completa. Incluye todos los números, fechas, nombres y detalles legales. No omitas nada."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                "max_tokens": 4000
            }
            
            # Aumentar timeout para procesamiento largo
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                error_detail = response.text
                raise Exception(f"Error {response.status_code} en DeepSeek API: {error_detail}")
            
            result = response.json()
            extracted_text = result['choices'][0]['message']['content']
            
            return extracted_text
            
        except requests.exceptions.Timeout:
            raise Exception("Timeout: La API de DeepSeek tardó demasiado en responder")
        except Exception as e:
            raise Exception(f"Error en OCR DeepSeek: {str(e)}")
    
    def get_mode_info(self):
        """Retorna información sobre el modo de operación actual"""
        if self.use_local:
            return f"Modo Local (Ollama) - Modelo: {self.ollama_model}"
        else:
            return "Modo API (DeepSeek Cloud)"


class TranslationClient:
    """Cliente para traducción de textos usando LLM local"""
    
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.model = Config.TRANSLATION_MODEL
    
    def translate_to_spanish(self, text, page_num=None):
        """Traduce texto a español, detectando el idioma automáticamente"""
        print(f"[DEBUG TRANSLATOR] translate_to_spanish llamado para página {page_num}")
        print(f"[DEBUG TRANSLATOR] Longitud del texto: {len(text)} caracteres")
        try:
            if not text or not text.strip():
                print(f"[DEBUG TRANSLATOR] Texto vacío, retornando sin traducir")
                return text
            
            print(f"[DEBUG TRANSLATOR] Enviando texto al LLM para traducción...")
            
            # Dejar que el LLM detecte el idioma y traduzca si es necesario
            prompt = f"""Detecta el idioma del siguiente texto. 
Si está en español, devuélvelo exactamente igual sin cambios.
Si está en otro idioma, tradúcelo al español.
Solo responde con el texto (original si es español, o traducido si es otro idioma), sin explicaciones.

Texto:
{text}"""
            
            if page_num:
                print(f"[INFO] Traduciendo página {page_num}...")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutos por traducción
            )
            
            if response.status_code != 200:
                print(f"[ERROR] Error en traducción: {response.status_code}")
                return text  # Devolver original si falla
            
            result = response.json()
            translated_text = result.get('response', '').strip()
            
            if translated_text:
                return translated_text
            else:
                print(f"[WARN] Traducción vacía, usando texto original")
                return text
                
        except requests.exceptions.Timeout:
            print(f"[ERROR] Timeout en traducción de página {page_num}")
            return text
        except Exception as e:
            print(f"[ERROR] Error en traducción: {str(e)}")
            return text
    
    def _is_likely_spanish(self, text):
        """Heurística mejorada para detectar si el texto probablemente está en español"""
        # Eliminar encabezados del sistema antes de analizar
        system_headers = [
            "DOCUMENTO OPTIMIZADO - EXTRACTO DE TEXTO",
            "=== PÁGINA",
            "---"
        ]
        
        clean_text = text
        for header in system_headers:
            clean_text = clean_text.replace(header, "")
        
        # Tomar solo las primeras líneas reales de contenido
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        if lines:
            clean_text = ' '.join(lines[:50])  # Primeras 50 líneas
        
        print(f"[DEBUG] Texto limpio para análisis: {clean_text[:200]}...")
        
        # Palabras EXCLUSIVAS del español (no en inglés)
        spanish_exclusive = ['señor', 'año', 'años', 'niño', 'sí', 'qué', 'cuál', 
                           'también', 'más', 'está', 'están', 'según', 'además',
                           'después', 'través', 'país', 'había', 'habían']
        
        # Palabras comunes en español
        spanish_common = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'una', 'los', 'las',
                         'del', 'al', 'con', 'por', 'para', 'su', 'sus', 'este', 'esta',
                         'ese', 'esa', 'pero', 'como', 'todo', 'todos', 'si', 'cuando',
                         'donde', 'muy', 'sin', 'sobre', 'entre', 'hasta', 'desde']
        
        # Palabras en inglés que ayudan a identificar que NO es español
        english_words = ['the', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has',
                        'been', 'this', 'that', 'with', 'from', 'they', 'their', 'there',
                        'invoice', 'date', 'number', 'amount', 'total', 'product', 'service',
                        'thank', 'you', 'your', 'our', 'business', 'company']
        
        text_lower = clean_text.lower()
        words = text_lower.split()[:200]  # Analizar primeras 200 palabras
        
        if len(words) < 5:
            return False  # Muy poco texto para determinar
        
        # Contar palabras exclusivas de español
        exclusive_count = sum(1 for word in words if any(excl in word for excl in spanish_exclusive))
        
        # Contar palabras en inglés
        english_count = sum(1 for word in words if word in english_words)
        
        # Contar palabras comunes en español
        spanish_count = sum(1 for word in words if word in spanish_common)
        
        # Buscar caracteres específicos del español
        has_spanish_chars = any(char in text for char in ['á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü', '¿', '¡'])
        
        # Decisión basada en múltiples factores
        print(f"[DEBUG] Palabras exclusivas español: {exclusive_count}")
        print(f"[DEBUG] Palabras en inglés: {english_count}")
        print(f"[DEBUG] Palabras comunes español: {spanish_count}")
        print(f"[DEBUG] Caracteres españoles: {has_spanish_chars}")
        
        # Si tiene palabras exclusivas de español O caracteres españoles, probablemente es español
        if exclusive_count > 0 or has_spanish_chars:
            return True
        
        # Si tiene muchas palabras en inglés, NO es español
        if english_count > len(words) * 0.2:  # Más del 20% en inglés
            return False
        
        # Si tiene muchas palabras comunes en español y pocas en inglés
        if spanish_count > len(words) * 0.3 and english_count < spanish_count:
            return True
        
        return False