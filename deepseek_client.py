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
            
            # Prompt mejorado para máxima extracción de texto
            prompt = """Extrae TODO el texto visible en esta imagen con máxima precisión. 
Instrucciones:
- Lee TODO el texto, incluyendo encabezados, párrafos, números, fechas y notas al pie
- Mantén el formato original y la estructura de párrafos
- No omitas nada, incluso texto pequeño o parcialmente visible
- Incluye TODOS los números, precios, fechas y referencias
- Si hay tablas, intenta mantener su estructura
- Devuelve el texto completo sin resumen ni comentarios adicionales

Texto:"""
            
            # Payload para Ollama (configuración optimizada para OCR)
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Baja temperatura para respuestas más precisas
                    "num_ctx": 8192,     # Contexto extendido para documentos largos
                    "num_predict": 4096  # Más tokens de salida para textos largos
                }
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
            
            # Prompt mejorado siguiendo las mejores prácticas de DeepSeek-OCR
            # Formato: <image>\n<|grounding|>... para documentos estructurados
            # o <image>\nFree OCR... para extracción simple de texto
            ocr_prompt = """<image>
<|grounding|>Extrae TODO el texto de este documento con máxima precisión y completitud.

Instrucciones:
- Lee el texto completo: títulos, párrafos, listas, notas al pie, referencias
- Incluye TODOS los números: fechas, cantidades, precios, teléfonos, referencias
- Mantén la estructura: usa markdown para tablas si las hay
- No omitas texto pequeño, notas al margen o texto parcialmente visible
- Transcribe con precisión absoluta, sin resumir ni parafrasear
- Si hay elementos no textuales (logos, imágenes), solo extrae el texto

Devuelve el texto completo extraido:"""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": f"data:image/png;base64,{base64_image}"
                            },
                            {
                                "type": "text", 
                                "text": ocr_prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 8000,      # Aumentado para capturar más texto
                "temperature": 0.1       # Baja temperatura para precissión
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
    """Cliente para traducción de textos usando OpenAI API (primario) o LLM local (fallback)"""
    
    def __init__(self):
        # Configuración OpenAI
        self.use_openai = Config.USE_OPENAI_TRANSLATION
        self.openai_api_key = Config.OPENAI_API_KEY
        self.openai_model = Config.OPENAI_MODEL
        
        # Configuración Ollama (fallback)
        self.ollama_url = Config.OLLAMA_URL
        self.ollama_model = Config.TRANSLATION_MODEL
        
        # Verificar configuración
        if self.use_openai:
            if not self.openai_api_key:
                print("[WARN] OpenAI API key no configurada, usando Ollama local como único método")
                self.use_openai = False
            else:
                print(f"[INFO] Traducción: OpenAI {self.openai_model} (primario) + Ollama {self.ollama_model} (fallback)")
        else:
            print(f"[INFO] Traducción: Ollama {self.ollama_model} (único método)")
    
    def translate_to_spanish(self, text, page_num=None):
        """Traduce texto a español usando OpenAI primero, Ollama como fallback"""
        print(f"[DEBUG TRANSLATOR] translate_to_spanish llamado para página {page_num}")
        print(f"[DEBUG TRANSLATOR] Longitud del texto: {len(text)} caracteres")
        
        if not text or not text.strip():
            print(f"[DEBUG TRANSLATOR] Texto vacío, retornando sin traducir")
            return text
        
        # Intentar primero con OpenAI si está habilitado
        if self.use_openai:
            try:
                print(f"[INFO] Intentando traducción con OpenAI ({self.openai_model})...")
                translated = self._translate_with_openai(text, page_num)
                if translated and translated != text:
                    print(f"[SUCCESS] Traducción exitosa con OpenAI")
                    return translated
                else:
                    print(f"[WARN] OpenAI no tradujo o devolvió igual, intentando con Ollama...")
            except Exception as e:
                print(f"[WARN] Error en OpenAI: {str(e)}, usando Ollama como fallback...")
        
        # Fallback a Ollama local
        print(f"[INFO] Usando Ollama local para traducción...")
        return self._translate_with_ollama(text, page_num)
    
    def _translate_with_openai(self, text, page_num=None):
        """Traduce usando OpenAI API"""
        try:
            import openai
            
            if page_num:
                print(f"[INFO] Traduciendo página {page_num} con OpenAI...")
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un traductor profesional. Traduce el texto al español manteniendo el formato original. Si el texto ya está en español, devuélvelo sin cambios."
                    },
                    {
                        "role": "user",
                        "content": f"Traduce este texto al español:\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            translated_text = response.choices[0].message.content.strip()
            print(f"[DEBUG] OpenAI: Traducción completada ({len(translated_text)} caracteres)")
            return translated_text
            
        except ImportError:
            raise Exception("Librería 'openai' no instalada. Ejecuta: pip install openai")
        except Exception as e:
            raise Exception(f"Error en OpenAI API: {str(e)}")
    
    def _translate_with_ollama(self, text, page_num=None):
        """Traduce usando Ollama local (fallback o método único)"""
        print(f"[DEBUG TRANSLATOR] translate_to_spanish llamado para página {page_num}")
        print(f"[DEBUG TRANSLATOR] Longitud del texto: {len(text)} caracteres")
        try:
            if not text or not text.strip():
                print(f"[DEBUG TRANSLATOR] Texto vacío, retornando sin traducir")
                return text
            
            print(f"[DEBUG TRANSLATOR] Enviando texto al LLM para traducción...")
            
            # Prompt más directo y específico para traducción
            prompt = f"""Eres un traductor profesional. Tu tarea es TRADUCIR el siguiente texto al español.

REGLAS IMPORTANTES:
- Si el texto ya está en español, devuélvelo SIN CAMBIOS
- Si el texto está en inglés u otro idioma, TRADÚCELO AL ESPAÑOL
- NO agregues explicaciones, comentarios ni introducciones
- Solo devuelve el texto traducido o el original si ya está en español
- Mantén el formato y estructura del texto original

TEXTO A TRADUCIR:
{text}

TRADUCCIÓN AL ESPAÑOL:"""
            
            if page_num:
                print(f"[INFO] Traduciendo página {page_num}...")
            
            print(f"[DEBUG] Modelo usado para traducción: {self.ollama_model}")
            print(f"[DEBUG] URL Ollama: {self.ollama_url}")
            print(f"[DEBUG] Primeros 200 caracteres del texto: {text[:200]}...")
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4000
                }
            }
            
            print(f"[DEBUG] Enviando request a Ollama...")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutos por traducción
            )
            
            print(f"[DEBUG] Status code de respuesta: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en traducción: {response.status_code}")
                print(f"[ERROR] Respuesta: {response.text}")
                return text  # Devolver original si falla
            
            result = response.json()
            translated_text = result.get('response', '').strip()
            
            print(f"[DEBUG] Longitud texto original: {len(text)}")
            print(f"[DEBUG] Longitud texto traducido: {len(translated_text)}")
            print(f"[DEBUG] Primeros 200 caracteres traducidos: {translated_text[:200]}...")
            
            if translated_text:
                print(f"[SUCCESS] Traducción completada exitosamente")
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