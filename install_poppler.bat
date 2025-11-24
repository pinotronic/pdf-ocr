@echo off
echo Instalando Poppler para Windows...

:: Crear directorio
if not exist "C:\poppler" mkdir C:\poppler

:: Descargar poppler
echo Descargando Poppler...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/poppler-23.11.0-Linux.zip' -OutFile 'poppler.zip'"

:: Extraer
echo Extrayendo...
powershell -Command "Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\poppler\' -Force"

:: Limpiar
del poppler.zip

echo Poppler instalado en C:\poppler
echo Agregando al PATH...
setx PATH "%PATH%;C:\poppler\Library\bin"

echo Instalacion completada!
pause