"""
Estrategia para Estiramientos Ergonómicos de Cuello y Trapecio en el Puesto de Trabajo.
Altamente calibrada para evitar falsos positivos y guiar al usuario con el Coach animado
e indicadores visuales de dirección (Izquierda / Derecha / Arriba).
"""
import time
import math
import numpy as np
from typing import Dict, Any, Optional
from src.patterns.strategy import ExerciseStrategy
from src.patterns.observer import EventBus, AppEvent
from src.vision.geometry import calculate_slope_angle, detect_user_posture
from src.ui.coach_avatar import CoachAvatar
from src.config import AppConfig

class StretchStrategy(ExerciseStrategy):
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.event_bus = EventBus()
        self.tick = 0
        self.reset()

    @property
    def name(self) -> str:
        return "Estiramiento Ergonómico (Cuello & Hombros)"

    @property
    def category(self) -> str:
        return "estiramiento"

    def reset(self) -> None:
        self.step = 0 # 0: Cuello Izq, 1: Cuello Der, 2: Brazos Arriba
        self.hold_start_time = None
        self.hold_duration = 3.5 # Segundos de estiramiento sostenido por lado
        self.completed_stretches = 0
        self.feedback = "Inclina suavemente la cabeza hacia la izquierda"
        self.hold_progress = 0.0
        self.is_completed = False

    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        self.tick += 1
        h, w = frame_shape[:2]

        # Pose para el avatar según el paso actual
        if getattr(self, "is_completed", False):
            pose_key = "COMPLETED"
        else:
            pose_key = "CUELLO_IZQ" if self.step == 0 else ("CUELLO_DER" if self.step == 1 else "BRAZOS_ARRIBA")
        avatar_img = CoachAvatar.render_pose(pose_key, self.tick, size=(190, 190))

        if landmarks is None:
            return {
                "step": self.step,
                "direction": "LEFT" if self.step == 0 else ("RIGHT" if self.step == 1 else "UP"),
                "feedback": "Ponte frente a la cámara para iniciar el estiramiento",
                "hold_progress": 0.0,
                "completed": self.completed_stretches,
                "avatar_img": avatar_img,
                "is_stretching": False,
                "tilt_angle": 0.0
            }

        # Puntos: Nariz (0), Orejas (7, 8), Hombros (11, 12), Muñecas (15, 16)
        nose = landmarks[0]
        ear_l, ear_r = landmarks[7], landmarks[8]
        sh_l, sh_r = landmarks[11], landmarks[12]
        w_l, w_r = landmarks[15], landmarks[16]

        sh_mid_y = (sh_l.y + sh_r.y) / 2.0
        now = time.time()
        is_stretching = False

        # Las manos deben estar abajo para no confundir cuello con saludo
        hands_down = (w_l.y > sh_mid_y - 0.08) and (w_r.y > sh_mid_y - 0.08)

        # Inclinación angular relativa de las orejas respecto a los hombros
        ear_p1 = (ear_l.x * w, ear_l.y * h)
        ear_p2 = (ear_r.x * w, ear_r.y * h)
        sh_p1 = (sh_l.x * w, sh_l.y * h)
        sh_p2 = (sh_r.x * w, sh_r.y * h)

        ear_angle = calculate_slope_angle(ear_p1, ear_p2)
        sh_angle = calculate_slope_angle(sh_p1, sh_p2)
        true_tilt = abs(ear_angle - sh_angle)

        direction_code = "LEFT" if self.step == 0 else ("RIGHT" if self.step == 1 else "UP")

        if getattr(self, "is_completed", False):
            return {
                "step": self.step,
                "direction": "DONE",
                "feedback": "¡Estiramiento de cuello completado con éxito! 🎉",
                "hold_progress": 1.0,
                "hold_sec_remaining": 0.0,
                "completed": self.completed_stretches,
                "is_stretching": False,
                "is_completed": True,
                "tilt_angle": 0,
                "head_pt": (int(nose.x * w), int(nose.y * h)) if nose else None,
                "tick": self.tick,
                "avatar_img": avatar_img,
                "diagnosis": "Rutina cervical finalizada. Trapecios y cuello descargados."
            }

        if self.step == 0:
            # 1. Flecha izquierda en pantalla espejo (la cabeza se inclina hacia la izquierda: ear_r baja)
            left_tilted = (ear_r.y > ear_l.y + 0.030) and (true_tilt > 11.5)
            if left_tilted and hands_down:
                is_stretching = True
                self.feedback = "¡Perfecto! Mantén la inclinación hacia la izquierda..."
            else:
                self.feedback = "⬅ Inclina suavemente la cabeza hacia la flecha izquierda"

        elif self.step == 1:
            # 2. Flecha derecha en pantalla espejo (la cabeza se inclina hacia la derecha: ear_l baja)
            right_tilted = (ear_l.y > ear_r.y + 0.030) and (true_tilt > 11.5)
            if right_tilted and hands_down:
                is_stretching = True
                self.feedback = "¡Excelente! Mantén la inclinación hacia la derecha..."
            else:
                self.feedback = "➡ Ahora inclina la cabeza hacia la flecha derecha"

        elif self.step == 2:
            # 3. Brazos arriba para descompresión de columna (ambas muñecas claramente sobre la cabeza)
            arms_elevated = (w_l.y < nose.y - 0.08) and (w_r.y < nose.y - 0.08)
            if arms_elevated:
                is_stretching = True
                self.feedback = "¡Genial! Estira tus brazos hacia el cielo..."
            else:
                self.feedback = "⬆ Eleva ambos brazos bien alto y estira la espalda"

        # Barra de tiempo sostenido con tolerancia
        if is_stretching:
            self.last_matched_time = now
            if self.hold_start_time is None:
                self.hold_start_time = now
            elapsed = now - self.hold_start_time
            self.hold_progress = min(1.0, elapsed / self.hold_duration)

            if elapsed >= self.hold_duration:
                self.completed_stretches += 1
                self.hold_start_time = None
                self.hold_progress = 0.0

                if self.step >= 2:
                    # ¡Rutina completada! No reiniciar automáticamente
                    self.is_completed = True
                    self.event_bus.publish(AppEvent.REP_COMPLETED, {
                        "reps": self.completed_stretches,
                        "evaluation": "¡Rutina de Estiramiento Cervical finalizada con éxito! Tensión liberada."
                    })
                else:
                    self.step += 1
                    self.event_bus.publish(AppEvent.REP_COMPLETED, {
                        "reps": self.completed_stretches,
                        "evaluation": f"Paso {self.step}/3 completado. Excelente alineación."
                    })
        else:
            # Histeresis de 0.5s para no resetear por parpadeo
            if self.hold_start_time is not None and (now - getattr(self, "last_matched_time", 0)) < 0.5:
                elapsed = now - self.hold_start_time
                self.hold_progress = min(1.0, elapsed / self.hold_duration)
                is_stretching = True
            else:
                self.hold_start_time = None
                self.hold_progress = 0.0

        rem_sec = round(max(0.0, self.hold_duration - (now - self.hold_start_time)), 1) if (is_stretching and self.hold_start_time) else round(self.hold_duration, 1)

        head_pt = (int(nose.x * w), int(nose.y * h))

        posture_info = detect_user_posture(landmarks)

        return {
            "step": self.step,
            "direction": direction_code,
            "feedback": self.feedback,
            "hold_progress": self.hold_progress,
            "hold_sec_remaining": rem_sec,
            "completed": self.completed_stretches,
            "is_stretching": is_stretching,
            "is_completed": getattr(self, "is_completed", False),
            "tilt_angle": int(true_tilt),
            "head_pt": head_pt,
            "tick": self.tick,
            "avatar_img": avatar_img,
            "diagnosis": "Descompresión cervical y liberación de trapecio en progreso.",
            "user_posture": posture_info.get("label", "Buscando postura..."),
            "user_posture_icon": posture_info.get("icon", "👤"),
            "is_standing": posture_info.get("is_standing", False)
        }


    def get_summary(self) -> Dict[str, Any]:
        return {
            "rutina": self.name,
            "estiramientos_completados": self.completed_stretches,
            "beneficio": "Reducción significativa de tensión en cuello y hombros."
        }
