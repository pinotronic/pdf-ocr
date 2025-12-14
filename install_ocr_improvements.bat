@echo off
REM Script de instalación rápida de mejoras OCR
REM Ejecutar desde el directorio del proyecto

echo ========================================
echo Instalacion de Mejoras OCR
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "requirements.txt" (
    echo ERROR: No se encuentra requirements.txt
    echo Por favor ejecuta este script desde el directorio del proyecto
    pause
    exit /b 1
)

echo [1/3] Activando entorno virtual...
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
    echo Entorno virtual activado
) else (
    echo ADVERTENCIA: No se encuentra el entorno virtual en .\env
    echo Continuando con Python del sistema...
)
echo.

echo [2/3] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [3/3] Verificando instalacion...
python verify_ocr_improvements.py
echo.

echo ========================================
echo Instalacion completada
echo ========================================
echo.
echo Proximos pasos:
echo   1. Procesa un PDF de prueba
echo   2. Compara los resultados con versiones anteriores
echo   3. Ajusta configuracion en .env si es necesario
echo.
pause
