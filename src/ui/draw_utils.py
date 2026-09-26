"""
Utilidades gráficas para renderizar texto y banners con alto contraste.
Garantiza legibilidad absoluta frente a ropa blanca, fondos claros o poca iluminación.
"""
import cv2
import numpy as np

def draw_pill_text(frame: np.ndarray, text: str, pos: tuple,
                   font_scale: float = 0.65, text_color: tuple = (255, 255, 255),
                   bg_color: tuple = (18, 24, 36), padding: int = 8, thickness: int = 2) -> np.ndarray:
    """
    Dibuja un texto sobre una pastilla/caja oscura con opacidad para máxima legibilidad.
    """
    x, y = pos
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x1 = max(0, x - padding)
    y1 = max(0, y - th - padding)
    x2 = min(frame.shape[1], x + tw + padding)
    y2 = min(frame.shape[0], y + baseline + padding)

    # Crear recuadro oscuro semitransparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
    # Mezclar con 85% de opacidad para efecto glassmorphism
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    # Borde sutil
    cv2.rectangle(frame, (x1, y1), (x2, y2), (56, 189, 248), 1)

    # Dibujar texto nítido
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
    return frame

def draw_bottom_banner(frame: np.ndarray, text: str, accent_color: tuple = (34, 197, 94)) -> np.ndarray:
    """
    Dibuja un banner inferior translúcido estilo subtítulos modernos de streaming/TikTok.
    """
    h, w = frame.shape[:2]
    banner_h = 55
    y1 = h - banner_h
    y2 = h

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y1), (w, y2), (15, 23, 42), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

    # Línea superior de acento neón
    cv2.line(frame, (0, y1), (w, y1), accent_color, 2)

    # Texto centrado
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.65
    thickness = 2
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    tx = max(15, (w - tw) // 2)
    ty = y1 + ((banner_h + th) // 2) - 4

    cv2.putText(frame, text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return frame

def draw_progress_bar(frame: np.ndarray, pos: tuple, size: tuple, progress: float,
                      color: tuple = (34, 197, 94), bg_color: tuple = (30, 41, 59)) -> np.ndarray:
    """
    Dibuja una barra de progreso elegante con fondo semitransparente y borde.
    """
    x, y = pos
    w, h = size
    progress = max(0.0, min(1.0, progress))

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), bg_color, -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

    fill_w = int(w * progress)
    if fill_w > 0:
        cv2.rectangle(frame, (x, y), (x + fill_w, y + h), color, -1)

    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
    return frame

def draw_direction_indicator(frame: np.ndarray, direction: str, center_pt: tuple,
                             tick: int = 0, color: tuple = (56, 189, 248)) -> np.ndarray:
    """
    Dibuja una flecha animada y señal visual en pantalla indicando la dirección del movimiento.
    direction: 'LEFT', 'RIGHT', 'UP'
    """
    cx, cy = center_pt
    offset = int(np.sin(tick * 0.2) * 8)

    if direction == "LEFT":
        # Flecha apuntando a la izquierda
        start = (cx - 15 + offset, cy)
        end = (cx - 55 + offset, cy)
        cv2.arrowedLine(frame, start, end, color, 4, tipLength=0.35)
        cv2.circle(frame, (cx - 60 + offset, cy), 8, (255, 255, 255), 2)
    elif direction == "RIGHT":
        # Flecha apuntando a la derecha
        start = (cx + 15 + offset, cy)
        end = (cx + 55 + offset, cy)
        cv2.arrowedLine(frame, start, end, color, 4, tipLength=0.35)
        cv2.circle(frame, (cx + 60 + offset, cy), 8, (255, 255, 255), 2)
    elif direction == "UP":
        # Flecha apuntando hacia arriba
        start = (cx, cy - 15 + offset)
        end = (cx, cy - 55 + offset)
        cv2.arrowedLine(frame, start, end, color, 4, tipLength=0.35)
        cv2.circle(frame, (cx, cy - 60 + offset), 8, (255, 255, 255), 2)
    elif direction == "ANY":
        # Flechas a ambos lados indicando que cualquier hombro/lado es válido
        start_l = (cx - 15 - offset, cy)
        end_l = (cx - 48 - offset, cy)
        cv2.arrowedLine(frame, start_l, end_l, color, 3, tipLength=0.35)
        start_r = (cx + 15 + offset, cy)
        end_r = (cx + 48 + offset, cy)
        cv2.arrowedLine(frame, start_r, end_r, color, 3, tipLength=0.35)

    return frame

def draw_circular_countdown(frame: np.ndarray, center: tuple, radius: int,
                            progress: float, elapsed_sec: float, total_sec: float = 10.0,
                            is_matched: bool = False) -> np.ndarray:
    """
    Dibuja un contador circular estilizado para el estiramiento de muñecas.
    Cambia de rojo (no detectado) a verde neón (detectado) y se llena proporcionalmente.
    """
    cx, cy = center
    color = (34, 197, 94) if is_matched else (70, 70, 230)
    bg_ring = (40, 50, 70)

    # Anillo base
    cv2.circle(frame, (cx, cy), radius, bg_ring, 4, cv2.LINE_AA)

    # Arco de progreso
    if progress > 0.0:
        angle_deg = int(min(360, max(0, progress * 360)))
        # cv2.ellipse dibuja el arco
        cv2.ellipse(frame, (cx, cy), (radius, radius), -90, 0, angle_deg, color, 5, cv2.LINE_AA)

    # Texto con segundos restantes en el centro
    rem = max(0.0, total_sec - elapsed_sec)
    txt = f"{rem:.1f}s" if is_matched else f"{total_sec:.0f}s"
    (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    cv2.putText(frame, txt, (cx - tw // 2, cy + th // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

    status_txt = "EN POSICION" if is_matched else "ESTIRA BRAZO"
    (sw, _), _ = cv2.getTextSize(status_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
    cv2.putText(frame, status_txt, (cx - sw // 2, cy + radius + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)
    return frame

def draw_chest_expansion_bar(frame: np.ndarray, pos: tuple, size: tuple,
                             expansion_pct: float, tick: int = 0) -> np.ndarray:
    """
    Barra de 'Apertura de Postura' para Apertura de Pecho y Retracción Escapular.
    Al llenarse produce una animación de pulso verde expansivo.
    """
    x, y = pos
    w, h = size
    pct = max(0.0, min(1.0, expansion_pct))
    is_full = pct >= 0.85

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (18, 24, 38), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Color verde neón con pulso si está completa
    if is_full:
        pulse = int(abs(np.sin(tick * 0.25)) * 6)
        color = (34, 197, 94)
        # Borde expansivo pulsante
        cv2.rectangle(frame, (x - pulse, y - pulse), (x + w + pulse, y + h + pulse), (34, 197, 94), 2)
    else:
        color = (56, 189, 248)

    fill_w = int(w * pct)
    if fill_w > 0:
        cv2.rectangle(frame, (x, y), (x + fill_w, y + h), color, -1)

    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)

    # Texto
    lbl = f"APERTURA DE POSTURA: {int(pct * 100)}%"
    cv2.putText(frame, lbl, (x + 10, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
    return frame

def draw_torsion_guide(frame: np.ndarray, hip_pts: tuple, shoulder_pts: tuple,
                       is_twisted: bool = False) -> np.ndarray:
    """
    Dibuja la línea de cadera (fija/estática) y la línea de hombros (dinámica).
    La línea de hombros cambia a verde neón cuando el giro es adecuado.
    """
    if hip_pts and len(hip_pts) == 2:
        h1, h2 = hip_pts
        # Línea de cadera estática
        cv2.line(frame, h1, h2, (56, 189, 248), 3, cv2.LINE_AA)
        cv2.circle(frame, h1, 5, (56, 189, 248), -1)
        cv2.circle(frame, h2, 5, (56, 189, 248), -1)
        cv2.putText(frame, "CADERA FIJA", (h1[0] - 20, h1[1] + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (56, 189, 248), 1, cv2.LINE_AA)

    if shoulder_pts and len(shoulder_pts) == 2:
        s1, s2 = shoulder_pts
        sh_color = (34, 197, 94) if is_twisted else (245, 158, 11)
        cv2.line(frame, s1, s2, sh_color, 4, cv2.LINE_AA)
        cv2.circle(frame, s1, 6, sh_color, -1)
        cv2.circle(frame, s2, 6, sh_color, -1)
        lbl = "GIRO OPTIMO" if is_twisted else "ROTANDO..."
        cv2.putText(frame, lbl, (s1[0] - 20, s1[1] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, sh_color, 1, cv2.LINE_AA)
    return frame

def draw_warning_badge(frame: np.ndarray, text: str, pos: tuple) -> np.ndarray:
    """
    Dibuja una pastilla de advertencia sutil en amarillo/ámbar (ej: '⚠️ Baja el hombro').
    """
    x, y = pos
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 2
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x1 = max(0, x - 8)
    y1 = max(0, y - th - 8)
    x2 = min(frame.shape[1], x + tw + 8)
    y2 = min(frame.shape[0], y + baseline + 8)

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (245, 158, 11), 2)

    cv2.putText(frame, text, (x, y), font, font_scale, (251, 191, 36), thickness, cv2.LINE_AA)
    return frame


