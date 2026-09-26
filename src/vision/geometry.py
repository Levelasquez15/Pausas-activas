"""
Módulo de cálculo biomecánico y geometría articular.
Calcula ángulos entre 3 articulaciones (ej. Cadera - Rodilla - Tobillo) usando trigonometría.
"""
import numpy as np
from typing import Tuple, Optional

def calculate_angle_2d(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """
    Calcula el ángulo en grados formado por tres puntos (A -> B -> C), donde B es el vértice.
    Retorna un valor entre 0 y 180 grados.
    """
    a_arr = np.array(a)
    b_arr = np.array(b)
    c_arr = np.array(c)
    
    radians = np.arctan2(c_arr[1] - b_arr[1], c_arr[0] - b_arr[0]) - \
              np.arctan2(a_arr[1] - b_arr[1], a_arr[0] - b_arr[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360.0 - angle
        
    return float(angle)

def calculate_slope_angle(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calcula la inclinación en grados de la línea entre dos puntos (ej. hombro a hombro)."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = np.abs(np.degrees(np.arctan2(dy, dx)))
    return float(angle)

def detect_user_posture(landmarks) -> dict:
    """
    Determina si el usuario está sentado frente a su escritorio o de pie.
    Evalúa ángulos articulares de piernas si son visibles y relación de encuadre.
    """
    if landmarks is None:
        return {
            "posture": "DESCONOCIDO",
            "label": "Buscando postura...",
            "icon": "👤",
            "is_standing": False
        }

    pose_pts = landmarks.pose if hasattr(landmarks, "pose") else landmarks
    if pose_pts is None or len(pose_pts) < 13:
        return {
            "posture": "DESCONOCIDO",
            "label": "Buscando postura...",
            "icon": "👤",
            "is_standing": False
        }

    nose = pose_pts[0]
    sh_l, sh_r = pose_pts[11], pose_pts[12]
    sh_y = (sh_l.y + sh_r.y) / 2.0
    sh_w = abs(sh_l.x - sh_r.x)

    # 1. Si las piernas están claramente en cuadro (cuerpo entero)
    if len(pose_pts) > 28:
        hip_l, hip_r = pose_pts[23], pose_pts[24]
        knee_l, knee_r = pose_pts[25], pose_pts[26]
        ankle_l, ankle_r = pose_pts[27], pose_pts[28]
        knee_vis = max(getattr(knee_l, "visibility", 0) or 0, getattr(knee_r, "visibility", 0) or 0)
        ankle_vis = max(getattr(ankle_l, "visibility", 0) or 0, getattr(ankle_r, "visibility", 0) or 0)

        if knee_vis > 0.40 and ankle_vis > 0.30:
            if (getattr(knee_l, "visibility", 0) or 0) >= (getattr(knee_r, "visibility", 0) or 0):
                leg_angle = calculate_angle_2d((hip_l.x, hip_l.y), (knee_l.x, knee_l.y), (ankle_l.x, ankle_l.y))
            else:
                leg_angle = calculate_angle_2d((hip_r.x, hip_r.y), (knee_r.x, knee_r.y), (ankle_r.x, ankle_r.y))

            if leg_angle < 145.0:
                return {
                    "posture": "SENTADO",
                    "label": "Sentado en escritorio",
                    "icon": "🪑",
                    "is_standing": False
                }
            else:
                return {
                    "posture": "DE_PIE",
                    "label": "De pie",
                    "icon": "🧍",
                    "is_standing": True
                }

    # 2. Si las caderas están presentes
    if len(pose_pts) > 24:
        hip_l, hip_r = pose_pts[23], pose_pts[24]
        hip_y = (hip_l.y + hip_r.y) / 2.0
        torso_h = hip_y - sh_y
        if hip_y > 0.75 or nose.y > 0.25 or torso_h < 0.42:
            return {
                "posture": "SENTADO",
                "label": "Sentado en escritorio",
                "icon": "🪑",
                "is_standing": False
            }

    # 3. Encuadre típico de escritorio / webcam de laptop (cabeza y hombros en primer plano)
    if sh_w > 0.28 or sh_y > 0.40 or nose.y > 0.22:
        return {
            "posture": "SENTADO",
            "label": "Sentado en escritorio",
            "icon": "🪑",
            "is_standing": False
        }

    return {
        "posture": "DE_PIE",
        "label": "De pie",
        "icon": "🧍",
        "is_standing": True
    }
