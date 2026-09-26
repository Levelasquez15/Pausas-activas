@echo off
title Pausas Activas y Bienestar con IA
echo ============================================================
echo   INICIANDO PAUSAS ACTIVAS CON IA
echo ============================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] No se encontro Python en el sistema.
        echo Por favor ejecuta primero "instalar.bat" o instala Python 3.10+.
        echo.
        pause
        exit /b 1
    )
    set PY_CMD=py
) else (
    set PY_CMD=python
)

%PY_CMD% run.py

if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error al ejecutar la aplicacion.
    echo Asegurate de haber ejecutado "instalar.bat" previamente.
    pause
)
