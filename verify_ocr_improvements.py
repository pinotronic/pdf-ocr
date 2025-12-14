"""
Script para verificar que las mejoras de OCR están funcionando correctamente
"""
import sys
import os

def check_opencv():
    """Verifica que OpenCV esté instalado"""
    try:
        import cv2
        print(f"✓ OpenCV instalado: versión {cv2.__version__}")
        return True
    except ImportError:
        print("✗ OpenCV NO instalado")
        print("  Ejecuta: pip install opencv-python")
        return False

def check_numpy():
    """Verifica que numpy esté instalado"""
    try:
        import numpy as np
        print(f"✓ NumPy instalado: versión {np.__version__}")
        return True
    except ImportError:
        print("✗ NumPy NO instalado")
        print("  Ejecuta: pip install numpy")
        return False

def check_config():
    """Verifica la configuración"""
    try:
        from config import Config
        print(f"\n📋 Configuración actual:")
        print(f"  - IMAGE_DPI: {Config.IMAGE_DPI}")
        print(f"  - ENHANCE_IMAGE_QUALITY: {Config.ENHANCE_IMAGE_QUALITY}")
        print(f"  - IMAGE_SCALE_FACTOR: {Config.IMAGE_SCALE_FACTOR}")
        return True
    except Exception as e:
        print(f"✗ Error al leer configuración: {e}")
        return False

def test_image_enhancement():
    """Prueba básica de preprocesamiento de imagen"""
    try:
        import cv2
        import numpy as np
        from pdf_processor import PDFProcessor
        
        # Crear imagen de prueba
        print("\n🧪 Probando preprocesamiento de imagen...")
        test_image = np.ones((500, 700), dtype=np.uint8) * 255
        cv2.putText(test_image, "TEXTO DE PRUEBA", (50, 250), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        # Guardar imagen temporal
        import tempfile
        temp_dir = tempfile.mkdtemp()
        test_path = os.path.join(temp_dir, "test.png")
        cv2.imwrite(test_path, test_image)
        
        # Probar preprocesamiento
        processor = PDFProcessor()
        enhanced_path = processor.enhance_image_for_ocr(test_path)
        
        if os.path.exists(enhanced_path):
            print(f"✓ Preprocesamiento funcionando correctamente")
            print(f"  Imagen original: {test_path}")
            print(f"  Imagen mejorada: {enhanced_path}")
            
            # Limpiar
            os.remove(test_path)
            os.remove(enhanced_path)
            os.rmdir(temp_dir)
            return True
        else:
            print("✗ El preprocesamiento no generó imagen de salida")
            return False
            
    except Exception as e:
        print(f"✗ Error en prueba de preprocesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🔍 Verificación de Mejoras OCR")
    print("=" * 60)
    
    checks = []
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias:")
    checks.append(check_opencv())
    checks.append(check_numpy())
    
    # Verificar configuración
    checks.append(check_config())
    
    # Prueba de preprocesamiento (solo si todo lo anterior pasó)
    if all(checks):
        checks.append(test_image_enhancement())
    
    # Resumen
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("\nEl sistema está listo para usar las mejoras de OCR.")
        print("\nPróximos pasos:")
        print("  1. Procesa un PDF de prueba")
        print("  2. Compara los resultados con versiones anteriores")
        print("  3. Ajusta IMAGE_SCALE_FACTOR si es necesario")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("\nPor favor instala las dependencias faltantes:")
        print("  pip install -r requirements.txt")
    print("=" * 60)
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
