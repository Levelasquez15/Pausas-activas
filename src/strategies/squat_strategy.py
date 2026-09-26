"""
Estrategia para sentadillas (Squats) bajo el Patrón Strategy.
Monitorea los ángulos articulares de cadera-rodilla-tobillo en tiempo real,
cuenta repeticiones completas, valida la calidad biomecánica y genera diagnósticos
de mejora física según el volumen y técnica alcanzados.
"""
from typing import Dict, Any, Optional
import numpy as np
from src.patterns.strategy import ExerciseStrategy
from src.patterns.observer import EventBus, AppEvent
from src.vision.geometry import calculate_angle_2d, detect_user_posture
from src.ui.coach_avatar import CoachAvatar
from src.config import AppConfig

class SquatStrategy(ExerciseStrategy):
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.event_bus = EventBus()
        self.tick = 0
        self.reset()

    @property
    def name(self) -> str:
        return "Sentadillas Activas (Squats)"

    @property
    def category(self) -> str:
        return "fisica"

    def reset(self) -> None:
        self.reps_count = 0
        self.target_reps = 10
        self.is_completed = False
        self.stage = "UP"  # "UP" o "DOWN"
        self.current_angle = 180.0
        self.lowest_angle_in_rep = 180.0
        self.good_form_reps = 0
        self.feedback_message = "Párate erguido para comenzar"
        self.feedback_color = (255, 255, 255) # Blanco

    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        self.tick += 1
        h, w = frame_shape[:2]

        if getattr(self, "is_completed", False):
            avatar_img = CoachAvatar.render_pose("COMPLETED", self.tick, size=(190, 190))
            return {
                "reps": self.reps_count,
                "target_reps": self.target_reps,
                "angle": 180,
                "stage": "UP",
                "feedback": f"🎉 ¡Excelente! Completaste tu serie de {self.reps_count} sentadillas.",
                "progress_pct": 100,
                "good_form_reps": self.good_form_reps,
                "evaluation": self.get_fitness_evaluation(),
                "feedback_color": (34, 197, 94),
                "is_completed": True,
                "avatar_img": avatar_img
            }

        if landmarks is None:
            avatar_img = CoachAvatar.render_pose("SENTADILLA", self.tick, size=(190, 190))
            return {
                "reps": self.reps_count,
                "target_reps": self.target_reps,
                "angle": self.current_angle,
                "stage": self.stage,
                "feedback": "Cuerpo no detectado en cámara",
                "progress_pct": 0,
                "feedback_color": (150, 150, 150),
                "is_completed": False,
                "avatar_img": avatar_img
            }

        h, w = frame_shape[:2]

        # Extraer puntos de pierna izquierda y derecha
        # Usamos la pierna que tenga mejor visibilidad
        hip_l, knee_l, ankle_l = landmarks[23], landmarks[25], landmarks[27]
        hip_r, knee_r, ankle_r = landmarks[24], landmarks[26], landmarks[28]

        vis_l = (hip_l.visibility or 0) + (knee_l.visibility or 0) + (ankle_l.visibility or 0)
        vis_r = (hip_r.visibility or 0) + (knee_r.visibility or 0) + (ankle_r.visibility or 0)

        if vis_l >= vis_r:
            hip = (hip_l.x * w, hip_l.y * h)
            knee = (knee_l.x * w, knee_l.y * h)
            ankle = (ankle_l.x * w, ankle_l.y * h)
        else:
            hip = (hip_r.x * w, hip_r.y * h)
            knee = (knee_r.x * w, knee_r.y * h)
            ankle = (ankle_r.x * w, ankle_r.y * h)

        # Calcular ángulo articular de la rodilla
        angle = calculate_angle_2d(hip, knee, ankle)
        self.current_angle = angle

        # Barra de progreso de flexión: 160° = 0%, 90° = 100%
        progress_pct = int(np.interp(angle, [self.config.SQUAT_DOWN_ANGLE, self.config.SQUAT_UP_ANGLE], [100, 0]))
        progress_pct = max(0, min(100, progress_pct))

        # Lógica de estados de la repetición
        if angle <= self.config.SQUAT_DOWN_ANGLE:
            if self.stage == "UP":
                self.stage = "DOWN"
                self.lowest_angle_in_rep = angle
                self.feedback_message = "¡Buena profundidad! Ahora sube"
                self.feedback_color = (34, 197, 94) # Verde
            else:
                self.lowest_angle_in_rep = min(self.lowest_angle_in_rep, angle)

        elif angle >= self.config.SQUAT_UP_ANGLE:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.reps_count += 1
                if self.lowest_angle_in_rep <= 95.0:
                    self.good_form_reps += 1
                    self.feedback_message = f"¡Excelente repetición #{self.reps_count}!"
                    self.feedback_color = (34, 197, 94)
                else:
                    self.feedback_message = f"Repetición #{self.reps_count}: Intenta bajar un poco más"
                    self.feedback_color = (245, 158, 11)

                # Notificar a los observadores (para sonido y contador)
                self.event_bus.publish(AppEvent.REP_COMPLETED, {
                    "reps": self.reps_count,
                    "depth_angle": self.lowest_angle_in_rep,
                    "evaluation": self.get_fitness_evaluation()
                })

                if self.reps_count >= self.target_reps:
                    self.is_completed = True
                    self.feedback_message = f"🎉 ¡Excelente! Completaste tu serie de {self.reps_count} sentadillas."
            else:
                if self.reps_count == 0:
                    self.feedback_message = "Listo: Flexiona rodillas y baja caderas"
                    self.feedback_color = (56, 189, 248) # Celeste

        self.tick += 1
        pose_k = "COMPLETED" if self.is_completed else "SENTADILLA"
        avatar_img = CoachAvatar.render_pose(pose_k, self.tick, size=(190, 190))

        posture_info = detect_user_posture(landmarks)

        return {
            "reps": self.reps_count,
            "target_reps": self.target_reps,
            "angle": int(self.current_angle),
            "stage": self.stage,
            "feedback": self.feedback_message,
            "progress_pct": progress_pct,
            "good_form_reps": self.good_form_reps,
            "evaluation": self.get_fitness_evaluation(),
            "feedback_color": self.feedback_color,
            "is_completed": self.is_completed,
            "avatar_img": avatar_img,
            "user_posture": posture_info.get("label", "Buscando postura..."),
            "user_posture_icon": posture_info.get("icon", "👤"),
            "is_standing": posture_info.get("is_standing", False)
        }

    def get_fitness_evaluation(self) -> str:
        """
        Determina cómo el número de sentadillas beneficia la condición física del usuario.
        """
        reps = self.reps_count
        if reps == 0:
            return "Comienza tu primera serie de activación muscular."
        elif reps < 5:
            return f"{reps} reps: Activando circulación sanguínea y descongestionando piernas."
        elif reps < 10:
            return f"{reps} reps: Estimulando glúteos y cuádriceps. Excelente reactivación tras estar sentado."
        elif reps < 15:
            return f"{reps} reps: Nivel saludable. Disminuyes rigidez articular y quemas glucosa activa."
        elif reps < 25:
            return f"{reps} reps: ¡Gran resistencia muscular! Mejoras postura lumbar y tonicidad física."
        else:
            return f"{reps} reps: ¡Nivel avanzado! Excelente potencia y acondicionamiento cardiovascular."

    def get_summary(self) -> Dict[str, Any]:
        return {
            "rutina": self.name,
            "repeticiones_totales": self.reps_count,
            "repeticiones_perfectas": self.good_form_reps,
            "calorias_estimadas": round(self.reps_count * 0.32, 1),
            "diagnostico_fisico": self.get_fitness_evaluation()
        }
