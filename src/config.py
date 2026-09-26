"""
Configuración central de la aplicación de Pausas Activas y Salud en el Trabajo.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AppConfig:
    # Ventana y Rendimiento
    WINDOW_TITLE: str = "Pausas Activas IA - Bienestar & Ergonomía"
    WINDOW_WIDTH: int = 1320
    WINDOW_HEIGHT: int = 780
    FPS_TARGET: int = 30
    
    # Cámara
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    
    # Tiempos de Pausas Activas (en minutos)
    WORK_INTERVAL_MINUTES: int = 45   # Alerta de pausa cada 45 minutos
    BREAK_DURATION_MINUTES: int = 3    # Duración de la pausa activa
    
    # Umbrales Biomecánicos para Sentadillas
    SQUAT_UP_ANGLE: float = 160.0      # De pie (ángulo cadera-rodilla-tobillo)
    SQUAT_DOWN_ANGLE: float = 90.0     # Sentadilla válida (profunda)
    SQUAT_MIN_ANGLE: float = 75.0      # Sentadilla óptima / límite de seguridad
    
    # Parámetros de Respiración (Segundos)
    TRIANGLE_INHALE: float = 3.5
    TRIANGLE_HOLD: float = 3.5
    TRIANGLE_EXHALE: float = 3.5
    
    TECH_478_INHALE: float = 4.0
    TECH_478_HOLD: float = 7.0
    TECH_478_EXHALE: float = 8.0
    
    # Paleta de Colores - Sistema de Diseño Limpio (Inspirado en Refero / Linear / Raycast)
    COLOR_BG_DARK: str = "#090D16"         # Fondo base midnight profundo
    COLOR_BG_SIDEBAR: str = "#080B12"      # Fondo barra lateral con contraste sutil
    COLOR_SURFACE: str = "#111726"         # Superficie de tarjetas y módulos
    COLOR_SURFACE_HOVER: str = "#182236"   # Elevación hover sutil
    COLOR_BORDER_SUBTLE: str = "#1C2638"   # Borde fino de 1px
    COLOR_BORDER_STRONG: str = "#2B3952"   # Borde para estado activo / seleccionado
    
    # Acentos y Semántica
    COLOR_ACCENT_PRIMARY: str = "#3B82F6"  # Azul eléctrico Linear/Raycast
    COLOR_ACCENT_SUCCESS: str = "#10B981"  # Verde esmeralda (salud, técnica correcta, progreso)
    COLOR_ACCENT_ZEN: str = "#38BDF8"      # Celeste calma y respiración
    COLOR_ACCENT_WARNING: str = "#F59E0B"  # Ámbar alerta/corrección postural
    COLOR_ACCENT_DANGER: str = "#EF4444"   # Rojo detener/alerta crítica
    
    # Jerarquía Tipográfica
    COLOR_TEXT_MAIN: str = "#F8FAFC"       # Blanco de alto contraste para titulares y métricas
    COLOR_TEXT_SECONDARY: str = "#94A3B8"  # Gris balanceado para lectura de instrucciones
    COLOR_TEXT_MUTED: str = "#64748B"      # Gris tenue para etiquetas y metadatos

