"""
Estrategia para Respiraciones Conscientes y Mindfulness bajo el Patrón Strategy.
Implementa las técnicas de relajación (Respiración Triangular, 4-7-8 y Respiración Consciente
con Corrección Postural mediante MediaPipe).
"""
import time
from typing import Dict, Any, Optional
from src.patterns.strategy import ExerciseStrategy
from src.patterns.observer import EventBus, AppEvent
from src.vision.geometry import calculate_slope_angle
from src.config import AppConfig

class BreathingStrategy(ExerciseStrategy):
    def __init__(self, mode: str = "triangular", config: Optional[AppConfig] = None):
        """
        mode: 'triangular' (TikTok: Inhala -> Mantén -> Exhala)
              '478' (TikTok: 4s Inhala -> 7s Mantén -> 8s Exhala)
              'consciente' (Con corrección de postura en cámara)
        """
        self.mode = mode
        self.config = config or AppConfig()
        self.event_bus = EventBus()
        self.reset()

    @property
    def name(self) -> str:
        if self.mode == "triangular":
            return "Respiración Triangular (Anti-Estrés Rápido)"
        elif self.mode == "478":
            return "Técnica 4-7-8 (Despejar Mente y Ansiedad)"
        else:
            return "Respiración Consciente & Postural"

    @property
    def category(self) -> str:
        return "respiracion"

    def set_mode(self, mode: str):
        self.mode = mode
        self.reset()

    def reset(self) -> None:
        self.cycles_completed = 0
        self.is_completed = False
        self.phase_start_time = time.time()
        self.current_phase_index = 0
        self.current_phase_name = "INHALA"
        self.phase_duration = self._get_current_phase_duration()
        self.posture_status = "Esperando postura..."
        self.posture_correct = True
        self.total_breaths_target = 3

    def _get_phases(self):
        if self.mode == "triangular":
            # 3 lados iguales del triángulo (ej. 3.5 segundos cada uno)
            return [
                ("INHALA", self.config.TRIANGLE_INHALE, "Inhala profundamente por la nariz"),
                ("MANTÉN", self.config.TRIANGLE_HOLD, "Sostén el aire con calma"),
                ("EXHALA", self.config.TRIANGLE_EXHALE, "Exhala lentamente por la boca")
            ]
        elif self.mode == "478":
            return [
                ("INHALA (4s)", self.config.TECH_478_INHALE, "Inhala suave por la nariz"),
                ("MANTÉN (7s)", self.config.TECH_478_HOLD, "Retén el aire, relaja el cuerpo"),
                ("EXHALA (8s)", self.config.TECH_478_EXHALE, "Exhala todo el aire por la boca")
            ]
        else: # consciente
            return [
                ("INHALA", 4.0, "Inhala sintiendo cómo se expande el abdomen"),
                ("EXHALA", 5.0, "Exhala soltando toda la tensión de los hombros")
            ]

    def _get_current_phase_duration(self) -> float:
        phases = self._get_phases()
        return phases[self.current_phase_index % len(phases)][1]

    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        """
        Calcula el progreso en la figura geométrica y evalúa la postura en cámara.
        """
        if getattr(self, "is_completed", False):
            return {
                "mode": self.mode,
                "phase_name": "¡COMPLETADO!",
                "phase_index": 0,
                "total_phases": 3,
                "phase_progress": 1.0,
                "remaining_seconds": 0.0,
                "instruction": "🎉 ¡Sesión de respiración completada! Mente despejada y ritmo cardíaco en calma.",
                "cycles_completed": self.cycles_completed,
                "target_cycles": self.total_breaths_target,
                "posture_status": "Excelente: postura y respiración alineadas.",
                "posture_correct": True,
                "is_completed": True,
                "mental_benefit": self.get_mental_benefit()
            }

        now = time.time()
        elapsed = now - self.phase_start_time
        phases = self._get_phases()
        current_phase_tuple = phases[self.current_phase_index]
        self.current_phase_name = current_phase_tuple[0]
        self.phase_duration = current_phase_tuple[1]
        phase_instruction = current_phase_tuple[2]

        # Verificar si terminó la fase actual
        if elapsed >= self.phase_duration:
            self.current_phase_index = (self.current_phase_index + 1) % len(phases)
            self.phase_start_time = now
            elapsed = 0.0

            # Si regresamos a la primera fase, se completó 1 ciclo completo
            if self.current_phase_index == 0:
                self.cycles_completed += 1
                self.event_bus.publish(AppEvent.BREATH_CYCLE_DONE, {
                    "cycles": self.cycles_completed,
                    "mode": self.mode
                })
                if self.cycles_completed >= self.total_breaths_target:
                    self.is_completed = True

            new_phase = phases[self.current_phase_index]
            self.current_phase_name = new_phase[0]
            self.phase_duration = new_phase[1]
            phase_instruction = new_phase[2]
            
            self.event_bus.publish(AppEvent.BREATH_PHASE_CHANGE, {
                "phase": self.current_phase_name,
                "cycles": self.cycles_completed
            })

        # Progreso de la fase actual (de 0.0 a 1.0)
        phase_progress = min(1.0, elapsed / self.phase_duration)
        remaining_seconds = max(0.0, self.phase_duration - elapsed)

        # Evaluación de postura con MediaPipe si hay cámara activa
        if landmarks is not None:
            h, w = frame_shape[:2]
            # Puntos de hombros (11 izq, 12 der) y nariz (0)
            sh_l = (landmarks[11].x * w, landmarks[11].y * h)
            sh_r = (landmarks[12].x * w, landmarks[12].y * h)
            nose = (landmarks[0].x * w, landmarks[0].y * h)

            # Inclinación de hombros (si están desnivelados)
            shoulder_tilt = calculate_slope_angle(sh_l, sh_r)
            shoulder_mid_x = (sh_l[0] + sh_r[0]) / 2.0

            # Cabeza centrada
            head_offset = abs(nose[0] - shoulder_mid_x)

            if shoulder_tilt > 8.0:
                self.posture_status = "Nivela tus hombros para relajar el trapecio"
                self.posture_correct = False
            elif head_offset > 40:
                self.posture_status = "Centra tu cabeza y mantén la mirada al frente"
                self.posture_correct = False
            else:
                self.posture_status = "Postura correcta: Espalda erguida y respiración fluida"
                self.posture_correct = True
        else:
            self.posture_status = "Mantén la espalda recta y las manos relajadas"
            self.posture_correct = True

        return {
            "mode": self.mode,
            "phase_name": self.current_phase_name,
            "phase_index": self.current_phase_index,
            "total_phases": len(phases),
            "phase_progress": phase_progress,
            "remaining_seconds": round(remaining_seconds, 1),
            "instruction": phase_instruction,
            "cycles_completed": self.cycles_completed,
            "target_cycles": self.total_breaths_target,
            "posture_status": self.posture_status,
            "posture_correct": self.posture_correct,
            "mental_benefit": self.get_mental_benefit()
        }

    def get_mental_benefit(self) -> str:
        cycles = self.cycles_completed
        if cycles < 2:
            return "Activando respuesta parasimpática (reducción de frecuencia cardíaca)."
        elif cycles < 5:
            return "Bajando niveles de cortisol (estrés laboral) y oxigenando corteza prefrontal."
        elif cycles < 8:
            return "Mayor claridad mental y alivio de la sobrecarga cognitiva en el trabajo."
        else:
            return "¡Estado de calma profunda alcanzado! Sistema nervioso restaurado."

    def get_summary(self) -> Dict[str, Any]:
        return {
            "rutina": self.name,
            "ciclos_completados": self.cycles_completed,
            "modo": self.mode,
            "beneficio_alcanzado": self.get_mental_benefit()
        }
