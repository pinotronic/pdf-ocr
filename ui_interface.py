import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import time
from pdf_processor import PDFProcessor
from config import Config

class PDFOptimizerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de PDF con DeepSeek OCR")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.processor = PDFProcessor()
        self.current_progress = 0
        self.max_progress = 0
        self.is_processing = False
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Optimizador de PDF con IA", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # Mostrar modo de operación
        mode_info = self.processor.deepseek.get_mode_info()
        mode_label = ttk.Label(main_frame, 
                              text=mode_info, 
                              font=("Arial", 9),
                              foreground="#666666")
        mode_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Selección de archivo
        ttk.Label(main_frame, text="Archivo PDF:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path, width=50)
        file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        
        browse_btn = ttk.Button(main_frame, text="Examinar", command=self.browse_file)
        browse_btn.grid(row=2, column=2, pady=5)
        
        # Checkbox de traducción automática
        self.auto_translate = tk.BooleanVar(value=False)
        translate_check = ttk.Checkbutton(
            main_frame, 
            text="Traducir automáticamente al español",
            variable=self.auto_translate
        )
        translate_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Botón de procesamiento
        self.process_btn = ttk.Button(main_frame, 
                                     text="Optimizar PDF", 
                                     command=self.process_pdf,
                                     state="disabled")
        self.process_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(main_frame, text="Listo")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(10, 5))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Etiqueta de porcentaje
        self.percent_label = ttk.Label(main_frame, text="0%")
        self.percent_label.grid(row=6, column=3, padx=(10, 0))
        
        # Área de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Progreso y Resultados", padding="10")
        result_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_frame, height=12, width=80, state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para resultados
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Configurar expansión
        main_frame.rowconfigure(7, weight=1)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.process_btn.config(state="normal")
            self.log_result(f"📁 Archivo seleccionado: {os.path.basename(file_path)}")
            self.update_progress(0, "Listo para procesar")
    
    def update_progress(self, value, status=""):
        """Actualiza la barra de progreso y el texto de estado"""
        def update():
            self.progress['value'] = value
            self.percent_label.config(text=f"{int(value)}%")
            if status:
                self.status_label.config(text=status)
            self.root.update_idletasks()
        
        # Ejecutar en el hilo principal
        self.root.after(0, update)
    
    def process_pdf(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Por favor selecciona un archivo PDF")
            return
        
        # Deshabilitar botón durante el procesamiento
        self.process_btn.config(state="disabled")
        self.is_processing = True
        self.current_progress = 0
        
        # Limpiar resultados anteriores
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=self._process_pdf_thread)
        thread.daemon = True
        thread.start()
        
        # Iniciar actualización periódica del progreso
        self._update_progress_loop()
    
    def _update_progress_loop(self):
        """Actualiza el progreso periódicamente mientras se procesa"""
        if self.is_processing:
            # Simular progreso incremental si no hay actualizaciones reales
            if self.current_progress < 90:  # No pasar de 90% hasta que termine
                self.current_progress += 1
                self.update_progress(self.current_progress, "Procesando...")
            
            # Programar siguiente actualización
            self.root.after(500, self._update_progress_loop)
    
    def _process_pdf_thread(self):
        try:
            input_path = self.file_path.get()
            output_path = input_path.replace('.pdf', '_optimizado.pdf')
            
            # Configurar callback de progreso
            def progress_callback(stage, current, total, message=""):
                progress_map = {
                    "extracting": 10,
                    "processing": 40, 
                    "translating": 70,
                    "saving": 90,
                    "complete": 100
                }
                
                base_progress = progress_map.get(stage, 0)
                if current > 0 and total > 0:
                    stage_progress = (current / total) * 30  # 30% para cada etapa principal
                    self.current_progress = base_progress + stage_progress
                else:
                    self.current_progress = base_progress
                
                status_msg = f"{message} ({current}/{total})" if message else stage
                self.update_progress(self.current_progress, status_msg)
            
            self.log_result("🔄 Iniciando procesamiento...")
            self.update_progress(5, "Preparando...")
            
            # Obtener opción de traducción
            translate = self.auto_translate.get()
            print(f"[DEBUG UI] Checkbox de traducción: {translate}")
            if translate:
                self.log_result("🌐 Traducción automática activada")
            else:
                self.log_result("ℹ️ Traducción automática desactivada")
            
            print(f"[DEBUG UI] Llamando optimize_pdf con translate={translate}")
            # Procesar PDF con callback de progreso
            result = self.processor.optimize_pdf(input_path, output_path, progress_callback, translate=translate)
            
            # Completar progreso
            self.update_progress(100, "Completado!")
            
            # Actualizar UI en el hilo principal
            self.root.after(0, self._process_completed, result, output_path)
            
        except Exception as e:
            self.root.after(0, self._process_failed, str(e))
    
    def _process_completed(self, result, output_path):
        self.is_processing = False
        self.process_btn.config(state="normal")
        
        # Mostrar resultados
        self.log_result("✅ ¡Procesamiento completado!")
        self.log_result(f"📊 Método usado: {result.get('method', 'N/A')}")
        self.log_result(f"📄 Páginas procesadas: {result.get('pages_processed', 0)}")
        
        # Mostrar información de páginas fallidas si las hay
        failed_pages = result.get('failed_pages', [])
        if failed_pages:
            self.log_result(f"⚠️ Páginas con error: {', '.join(map(str, failed_pages))}")
        
        self.log_result(f"📦 Tamaño original: {result['original_size'] / 1024:.1f} KB")
        self.log_result(f"📦 Tamaño optimizado: {result['optimized_size'] / 1024:.1f} KB")
        self.log_result(f"🎯 Reducción: {result['compression_ratio']:.1f}%")
        self.log_result(f"💾 Archivo guardado: {os.path.basename(output_path)}")
        
        # Mostrar archivo de texto si existe
        text_file = result.get('text_file')
        if text_file:
            self.log_result(f"📝 Texto completo: {os.path.basename(text_file)}")
        
        # Mostrar archivo traducido si existe
        if result.get('translated'):
            translated_file = result.get('translated_text_file')
            if translated_file:
                self.log_result(f"🌐 Texto en español: {os.path.basename(translated_file)}")
        
        # Mostrar carpeta de progreso si existe
        progress_dir = result.get('progress_dir')
        if progress_dir and os.path.exists(progress_dir):
            num_files = len([f for f in os.listdir(progress_dir) if f.endswith('.txt')])
            self.log_result(f"📁 Archivos individuales: {num_files} páginas en {os.path.basename(progress_dir)}/")
        
        # Mensaje final
        if failed_pages:
            messagebox.showwarning("Completado con advertencias", 
                          f"PDF procesado pero con errores en {len(failed_pages)} página(s).\n"
                          f"Páginas con error: {', '.join(map(str, failed_pages))}\n"
                          f"Reducción: {result['compression_ratio']:.1f}%")
        else:
            messagebox.showinfo("Éxito", 
                          f"PDF optimizado creado exitosamente!\n"
                          f"Reducción: {result['compression_ratio']:.1f}%")
    
    def _process_failed(self, error_msg):
        self.is_processing = False
        self.process_btn.config(state="normal")
        self.update_progress(0, "Error")
        self.log_result(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", f"Ocurrió un error durante el procesamiento:\n{error_msg}")
    
    def log_result(self, message):
        def update_text():
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, message + "\n")
            self.result_text.see(tk.END)
            self.result_text.config(state=tk.DISABLED)
        
        self.root.after(0, update_text)
    
    def on_closing(self):
        self.is_processing = False
        self.processor.cleanup()
        self.root.destroy()