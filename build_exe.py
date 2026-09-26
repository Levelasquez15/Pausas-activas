"""
Script Automatizado para Generar el Ejecutable (.exe) de Pausas Activas.
Empaqueta MediaPipe, OpenCV, CustomTkinter, Pygame, los modelos de IA y assets.
"""
import os
import sys
import subprocess
import shutil

def build():
    print("=" * 65)
    print(" INICIANDO COMPILACIÓN DE EJECUTABLE (.EXE): PAUSAS ACTIVAS")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Obtener ruta de customtkinter para empaquetar temas y fuentes
    try:
        import customtkinter
        ctk_path = customtkinter.__path__[0]
    except ImportError:
        print("[ERROR] CustomTkinter no encontrado. Ejecuta: pip install -r requirements.txt")
        return False

    sep = ";" if sys.platform == "win32" else ":"

    # 2. Argumentos de PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=PausasActivas",
        "--windowed", # Sin consola negra de fondo
        "--noconfirm",
        "--clean",
        # Añadir carpetas de datos
        f"--add-data=models{sep}models",
        f"--add-data=assets{sep}assets",
        f"--add-data=data{sep}data",
        f"--add-data={ctk_path}{sep}customtkinter",
        # Hidden imports clave
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=customtkinter",
        "--hidden-import=mediapipe",
        "--hidden-import=pygame",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        # Punto de entrada
        "run.py"
    ]

    print("[1/3] Ejecutando PyInstaller con dependencias...")
    print(" ".join(cmd))
    ret = subprocess.run(cmd, cwd=base_dir)
    if ret.returncode != 0:
        print(f"[ERROR] La compilación falló con código {ret.returncode}")
        return False

    dist_exe = os.path.join(base_dir, "dist", "PausasActivas", "PausasActivas.exe")
    if os.path.exists(dist_exe):
        print("=" * 65)
        print(f"[ÉXITO] Ejecutable creado en: {dist_exe}")
        print("=" * 65)
        return True
    else:
        print("[AVISO] La compilación terminó pero no se encontró PausasActivas.exe en dist/")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
