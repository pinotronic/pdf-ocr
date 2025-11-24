import os
import tempfile
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from fpdf import FPDF
from deepseek_client import DeepSeekClient, TranslationClient
import platform
from config import Config

class PDFProcessor:
    def __init__(self):
        self.deepseek = DeepSeekClient()
        self.translator = TranslationClient()  # Siempre disponible
        self.temp_dir = tempfile.mkdtemp()
        self.poppler_path = self._find_poppler_aggressive()
    
    def _find_poppler_aggressive(self):
        """Búsqueda agresiva de poppler en el proyecto"""
        current_dir = os.getcwd()
        poppler_base = os.path.join(current_dir, "poppler")
        
        if not os.path.exists(poppler_base):
            return None
        
        # Posibles rutas según estructura típica
        possible_paths = [
            os.path.join(poppler_base, "Library", "bin"),
            os.path.join(poppler_base, "bin"),
            poppler_base,
        ]
        
        # Buscar archivos ejecutables clave
        key_files = ["pdftoppm.exe", "pdftoppm", "pdfinfo.exe", "pdfinfo"]
        
        for test_path in possible_paths:
            if os.path.exists(test_path):
                for file in key_files:
                    full_file_path = os.path.join(test_path, file)
                    if os.path.exists(full_file_path):
                        return test_path
        return None

    def extract_images_from_pdf(self, pdf_path, progress_callback=None):
        """Extrae imágenes de cada página del PDF"""
        if progress_callback:
            progress_callback("extracting", 0, 1, "Extrayendo imágenes del PDF...")
        
        try:
            if self.poppler_path:
                images = convert_from_path(
                    pdf_path, 
                    dpi=200, 
                    poppler_path=self.poppler_path
                )
            else:
                images = convert_from_path(pdf_path, dpi=200)
                
        except Exception as e:
            error_msg = f"Error al convertir PDF a imágenes: {str(e)}"
            raise Exception(error_msg)
        
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(self.temp_dir, f"page_{i+1}.png")
            
            # Optimizar imagen para OCR (formato PNG de calidad)
            # Convertir a RGB si es necesario (algunos PDFs pueden tener otros modos)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Guardar con buena calidad para OCR
            image.save(image_path, "PNG", optimize=False, compress_level=1)
            
            # Verificar tamaño del archivo (max 25MB recomendado por DeepSeek-OCR)
            file_size = os.path.getsize(image_path)
            if file_size > 25 * 1024 * 1024:  # 25MB
                print(f"[DEBUG] Página {i+1} muy grande ({file_size/1024/1024:.1f}MB), reduciendo calidad...")
                image.save(image_path, "PNG", optimize=True, quality=85)
            
            image_paths.append(image_path)
            
            if progress_callback:
                progress_callback("extracting", i+1, len(images), "Extrayendo imágenes...")
        
        return image_paths
    
    def extract_text_with_pypdf2(self, pdf_path):
        """Intenta extraer texto directamente del PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n\n"
            return text if text.strip() else None
        except:
            return None
    
    def optimize_pdf(self, input_pdf_path, output_pdf_path, progress_callback=None, translate=False):
        """Procesa y optimiza el PDF página por página, y traduce al final si es necesario"""
        print(f"[DEBUG PROCESSOR] optimize_pdf llamado con translate={translate}")
        try:
            # Verificar que el archivo de entrada existe
            if not os.path.exists(input_pdf_path):
                raise Exception(f"El archivo de entrada no existe: {input_pdf_path}")
            
            # Leer el PDF para obtener número de páginas
            reader = PdfReader(input_pdf_path)
            total_pages = len(reader.pages)
            
            # Crear carpeta para guardar progreso
            progress_dir = os.path.join(self.temp_dir, "progress")
            os.makedirs(progress_dir, exist_ok=True)
            
            # Extraer imágenes de cada página (para OCR si es necesario)
            if progress_callback:
                progress_callback("extracting", 0, total_pages, "Extrayendo páginas...")
            image_paths = self.extract_images_from_pdf(input_pdf_path, progress_callback)
            
            # Procesar cada página: texto directo o OCR
            extracted_texts = []
            failed_pages = []
            
            for i in range(total_pages):
                page_num = i + 1
                if progress_callback:
                    progress_callback("processing", i, total_pages, f"Procesando página {page_num}/{total_pages}")
                
                try:
                    # Intentar primero extraer texto directo de esta página
                    page = reader.pages[i]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        # Tiene texto directo
                        print(f"[INFO] Página {page_num}: Texto extraído directamente")
                        extracted_texts.append(page_text.strip())
                    else:
                        # No tiene texto, usar OCR
                        print(f"[INFO] Página {page_num}: Sin texto directo, usando OCR...")
                        if i < len(image_paths):
                            text = self.deepseek.extract_text_from_image(image_paths[i])
                            extracted_texts.append(text)
                        else:
                            extracted_texts.append("[ERROR: No se pudo procesar esta página]")
                            failed_pages.append(page_num)
                    
                    # Guardar progreso inmediatamente
                    progress_file = os.path.join(progress_dir, f"page_{page_num}.txt")
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== PÁGINA {page_num} ===\n\n")
                        f.write(extracted_texts[-1])
                        f.write("\n\n")
                    
                    print(f"[INFO] Página {page_num}/{total_pages} procesada y guardada")
                    
                except Exception as e:
                    error_msg = f"Error en página {page_num}: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    extracted_texts.append(f"[ERROR: {error_msg}]")
                    failed_pages.append(page_num)
            
            method = "hybrid"  # Puede ser combinación de directo + OCR
            pages_processed = len(extracted_texts)
            
            # TRADUCCIÓN AL FINAL (después de procesar todas las páginas)
            translated_texts = []
            if translate and self.translator:
                print(f"[INFO] Iniciando traducción de {len(extracted_texts)} páginas...")
                if progress_callback:
                    progress_callback("translating", 0, len(extracted_texts), "Traduciendo al español...")
                
                for i, text in enumerate(extracted_texts):
                    if "[ERROR" not in text:  # No traducir mensajes de error
                        print(f"[INFO] Traduciendo página {i+1}...")
                        translated = self.translator.translate_to_spanish(text, page_num=i+1)
                        translated_texts.append(translated)
                    else:
                        translated_texts.append(text)
                    
                    if progress_callback:
                        progress_callback("translating", i+1, len(extracted_texts), f"Traduciendo página {i+1}/{len(extracted_texts)}")
                
                print(f"[INFO] Traducción completada")
            else:
                print(f"[INFO] Traducción NO activada, usando textos originales")
                translated_texts = extracted_texts
            
            # Crear PDF optimizado
            if progress_callback:
                progress_callback("saving", 0, 1, "Guardando PDF optimizado...")
            
            # Usar textos traducidos si está habilitado
            texts_to_save = translated_texts if translate else extracted_texts
            self._create_optimized_pdf(texts_to_save, output_pdf_path, translated=translate)
            
            # Guardar archivo de texto consolidado (original)
            text_output_path = output_pdf_path.replace('.pdf', '_texto_completo.txt')
            with open(text_output_path, 'w', encoding='utf-8') as f:
                for i, text in enumerate(extracted_texts):
                    f.write(f"\n{'='*70}\n")
                    f.write(f"PÁGINA {i+1}\n")
                    f.write(f"{'='*70}\n\n")
                    f.write(text)
                    f.write("\n\n")
            
            # Si se tradujo, guardar también la versión traducida
            translated_text_path = None
            if translate and translated_texts != extracted_texts:
                translated_text_path = output_pdf_path.replace('.pdf', '_texto_ES.txt')
                with open(translated_text_path, 'w', encoding='utf-8') as f:
                    for i, text in enumerate(translated_texts):
                        f.write(f"\n{'='*70}\n")
                        f.write(f"PÁGINA {i+1} (ESPAÑOL)\n")
                        f.write(f"{'='*70}\n\n")
                        f.write(text)
                        f.write("\n\n")
            
            if progress_callback:
                progress_callback("saving", 1, 1, "PDF guardado")
            
            # Calcular compresión
            original_size = os.path.getsize(input_pdf_path)
            optimized_size = os.path.getsize(output_pdf_path)
            compression_ratio = (1 - optimized_size / original_size) * 100
            
            if progress_callback:
                progress_callback("complete", 1, 1, "Procesamiento completado")
            
            result = {
                "original_size": original_size,
                "optimized_size": optimized_size,
                "compression_ratio": compression_ratio,
                "pages_processed": pages_processed,
                "method": method,
                "failed_pages": failed_pages,
                "text_file": text_output_path,
                "progress_dir": progress_dir,
                "translated": translate,
                "translated_text_file": translated_text_path if translate else None
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error en procesamiento PDF: {str(e)}")
    
    def _create_optimized_pdf(self, texts, output_path, translated=False):
        """Crea PDF optimizado con el texto extraído"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Título del documento (solo si no está traducido)
        if not translated:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'DOCUMENTO OPTIMIZADO - EXTRACTO DE TEXTO', 0, 1, 'C')
            pdf.ln(10)
        
        for i, text in enumerate(texts):
            # Encabezado de página si hay múltiples textos
            if len(texts) > 1:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'--- Página {i+1} ---', 0, 1)
                pdf.ln(5)
            
            # Contenido
            pdf.set_font('Arial', '', 10)
            
            try:
                lines = text.split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            encoded_line = line.encode('latin-1', 'replace').decode('latin-1')
                        except:
                            encoded_line = line
                        
                        # Manejar líneas largas
                        if pdf.get_string_width(encoded_line) > 180:
                            words = encoded_line.split(' ')
                            current_line = ""
                            for word in words:
                                if pdf.get_string_width(current_line + word + ' ') <= 180:
                                    current_line += word + ' '
                                else:
                                    if current_line:
                                        pdf.cell(0, 6, current_line, 0, 1)
                                    current_line = word + ' '
                            if current_line:
                                pdf.cell(0, 6, current_line, 0, 1)
                        else:
                            pdf.cell(0, 6, encoded_line, 0, 1)
            except Exception as e:
                pdf.cell(0, 6, f"Error procesando texto: {str(e)}", 0, 1)
            
            pdf.ln(5)
        
        pdf.output(output_path)
    
    def cleanup(self):
        """Limpia archivos temporales"""
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass