@echo off
title Instalador de Pausas Activas con IA
echo ============================================================
echo   INSTALANDO DEPENDENCIAS DE PAUSAS ACTIVAS CON IA
echo ============================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] No se encontro Python instalado en el sistema.
        echo Por favor instala Python 3.10 o superior desde https://www.python.org/
        echo Asegurate de marcar la casilla "Add python.exe to PATH" durante la instalacion.
        echo.
        pause
        exit /b 1
    )
    set PY_CMD=py
) else (
    set PY_CMD=python
)

echo Usando: %PY_CMD%
echo Actualizando pip e instalando paquetes necesarios...
echo.
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   [EXITO] Dependencias instaladas correctamente.
    echo   Ya puedes iniciar el programa haciendo doble clic en:
    echo   "ejecutar.bat"
    echo ============================================================
) else (
    echo.
    echo [ADVERTENCIA] Ocurrio un inconveniente al instalar algunas dependencias.
    echo Revisa tu conexion a Internet o intenta ejecutar en la consola:
    echo py -m pip install -r requirements.txt
)
echo.
pause
