import os
import platform
import subprocess
import sys

def check_poppler():
    print("🔍 VERIFICACIÓN COMPLETA DE POPPLER")
    print("=" * 50)
    
    system = platform.system()
    current_dir = os.getcwd()
    poppler_dir = os.path.join(current_dir, "poppler")
    
    print(f"📂 Directorio actual: {current_dir}")
    print(f"📦 Sistema operativo: {system}")
    print(f"🔍 Ruta de poppler: {poppler_dir}")
    print()
    
    # Verificar si existe la carpeta poppler
    if not os.path.exists(poppler_dir):
        print("❌ ERROR: No se encuentra la carpeta 'poppler'")
        print("   La carpeta 'poppler' debe estar en el mismo directorio que los scripts")
        return None
    
    print("✅ Carpeta 'poppler' encontrada")
    
    # Listar contenido de la carpeta poppler
    print("\n📁 Contenido de la carpeta poppler:")
    try:
        for root, dirs, files in os.walk(poppler_dir):
            level = root.replace(poppler_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{subindent}{file}')
    except Exception as e:
        print(f"❌ Error al listar contenido: {e}")
    
    # Buscar archivos ejecutables clave
    print("\n🔎 Buscando archivos ejecutables de poppler...")
    
    # Archivos clave que debemos encontrar
    key_files = {
        "Windows": ["pdftoppm.exe", "pdfinfo.exe", "pdftocairo.exe"],
        "Linux": ["pdftoppm", "pdfinfo", "pdftocairo"],
        "Darwin": ["pdftoppm", "pdfinfo", "pdftocairo"]
    }
    
    files_to_find = key_files.get(system, [])
    found_files = []
    
    for root, dirs, files in os.walk(poppler_dir):
        for file in files:
            if file in files_to_find:
                full_path = os.path.join(root, file)
                found_files.append((file, full_path))
                print(f"✅ Encontrado: {file} -> {full_path}")
    
    # Determinar la ruta binaria
    bin_path = None
    if found_files:
        # Tomar el directorio del primer archivo encontrado
        first_file_path = found_files[0][1]
        bin_path = os.path.dirname(first_file_path)
        print(f"\n🎯 Ruta binaria detectada: {bin_path}")
    else:
        print("\n❌ No se encontraron los archivos ejecutables de poppler")
        print("   La carpeta poppler podría no tener la estructura correcta")
        return None
    
    # Probar la funcionalidad
    print("\n🧪 Probando funcionalidad de poppler...")
    test_pdf_path = os.path.join(current_dir, "test_poppler.pdf")
    try:
        # Crear un PDF de prueba simple
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "PDF de prueba para verificar poppler", 0, 1)
        pdf.output(test_pdf_path)
        print("✅ PDF de prueba creado")
        
        # Intentar convertir el PDF
        from pdf2image import convert_from_path
        
        images = convert_from_path(
            test_pdf_path, 
            dpi=100,  # Baja resolución para prueba rápida
            poppler_path=bin_path,
            first_page=1,
            last_page=1
        )
        
        print(f"✅ Conversión exitosa! Páginas convertidas: {len(images)}")
        
        # Limpiar archivos de prueba
        os.remove(test_pdf_path)
        for img in images:
            img.close()
            
        print("✅ Prueba completada exitosamente!")
        return bin_path
        
    except Exception as e:
        print(f"❌ Error en la prueba de funcionalidad: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        
        # Limpiar en caso de error
        if os.path.exists(test_pdf_path):
            try:
                os.remove(test_pdf_path)
            except:
                pass
        return None

def install_dependencies():
    """Instalar dependencias faltantes"""
    print("\n📦 VERIFICANDO DEPENDENCIAS...")
    try:
        import pdf2image
        print("✅ pdf2image está instalado")
    except ImportError:
        print("❌ pdf2image no está instalado, instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2image"])
        print("✅ pdf2image instalado")
    
    try:
        from fpdf import FPDF
        print("✅ fpdf está instalado")
    except ImportError:
        print("❌ fpdf no está instalado, instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf"])
        print("✅ fpdf instalado")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 50)
    
    # Instalar dependencias si faltan
    install_dependencies()
    
    print("\n" + "=" * 50)
    print("🔍 INICIANDO VERIFICACIÓN DE POPPLER")
    print("=" * 50)
    
    result = check_poppler()
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 CONFIGURACIÓN CORRECTA!")
        print(f"📍 Ruta de poppler a usar: {result}")
        print("\n📝 CONFIGURACIÓN PARA main.py:")
        print(f'   poppler_path = "{result}"')
    else:
        print("❌ HAY PROBLEMAS CON LA CONFIGURACIÓN")
        print("\n🔧 SOLUCIÓN:")
        print("1. Asegúrate de que la carpeta 'poppler' esté en el mismo directorio")
        print("2. Descarga la versión correcta desde:")
        print("   https://github.com/oschwartz10612/poppler-windows/releases")
        print("3. Extrae y renombra la carpeta a 'poppler'")
    
    print("=" * 50)
    input("\nPresiona Enter para salir...")