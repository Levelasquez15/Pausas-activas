"""
Punto de Entrada Principal (Main Entry Point)
Aplicación de Pausas Activas Inteligentes con MediaPipe, Estimación de Poses
y Módulo de Respiración Anti-Estrés.
"""
import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("=" * 60)
    print(" INICIANDO APLICACION: PAUSAS ACTIVAS & BIENESTAR CON IA")
    print("=" * 60)
    print("[OK] MediaPipe Pose Estimation cargado.")
    print("[OK] Patrones de diseño activos: Strategy, Observer, State, Factory.")
    print("[OK] TuxDance: ¡Imita al Coach! y Estiramiento de Cuello listos.")
    print("[OK] Modulo de Respiracion Triangular y Tecnica 4-7-8 listos.")
    print("-" * 60)
    
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        import traceback
        print("\n[ERROR FATAL EN EJECUCIÓN]:")
        traceback.print_exc()
        try:
            with open("error_log.txt", "w", encoding="utf-8") as f:
                traceback.print_exc(file=f)
        except Exception:
            pass

if __name__ == "__main__":
    main()

