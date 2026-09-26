"""
Estrategia Gamificada de Pausas Activas (TuxDance: Pausas Activas Ergonómicas).
Soporta el catálogo oficial de ejercicios ergonómicos con:
- Detección bilateral estricta (Lado 1 y Lado 2 obligatorios para muñecas, cuello, tríceps y torsión).
- Prevención de falsos positivos (los hombros y pecho exigen postura biomecánica real y no activan estando inmóvil).
- Sin colisiones de nombres ni TypeErrors.
"""
import time
import math
from typing import Dict, Any, Optional, List
from src.patterns.strategy import ExerciseStrategy
from src.patterns.observer import EventBus, AppEvent
from src.vision.geometry import calculate_angle_2d, calculate_slope_angle, detect_user_posture
from src.ui.coach_avatar import CoachAvatar
from src.ui.video_guide_player import VideoGuidePlayer
from src.storage.exercise_manager import ExerciseManager
from src.config import AppConfig

BILATERAL_TYPES = ["wrist_stretch", "hand_right", "hand_left", "neck_tilt", "neck_stretch", "triceps_stretch", "trunk_twist"]

class DanceGameStrategy(ExerciseStrategy):
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.event_bus = EventBus()
        self.exercise_manager = ExerciseManager()
        self.video_player = VideoGuidePlayer()
        self.tick = 0
        self.reset()

    @property
    def name(self) -> str:
        return "TuxDance: Pausas Ergonómicas con IA"

    @property
    def category(self) -> str:
        return "gamificacion"

    def reset(self) -> None:
        self.exercises = self.exercise_manager.get_all()
        self.current_step_index = 0
        self.score = 0
        self.combo = 0
        self.hold_start_time = None
        self.match_active = False
        self.completed_cycles = 0
        self.is_completed = False
        self.waiting_for_greeting = True
        self.waiting_for_finish_gesture = False
        self.finish_acknowledged = False

        # Estados bilaterales (Lado 1 y Lado 2 obligatorios)
        self.current_side_phase = 1
        self.side_1_detected = None
        self.side_switch_time = 0.0

        # Estados específicos para ejercicios
        self.calf_reps = 0
        self.calf_stage = "DOWN"
        self.calf_baseline_y = None
        self.last_rep_time = 0.0
        self.shoulder_hiking = False
        self.shoulder_neutral_y = None
        self.chest_expansion_pct = 0.0
        self.last_matched_time = 0.0

    def reload_exercises(self):
        """Recarga la lista de ejercicios si el usuario agregó o editó alguno."""
        self.exercises = self.exercise_manager.get_all()
        if self.current_step_index >= len(self.exercises):
            self.current_step_index = 0

    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        self.tick += 1
        frame_h, frame_w = frame_shape[:2]
        if not self.exercises:
            self.exercises = self.exercise_manager.get_all()

        # Si la rutina ya fue completada, esperar el gesto de desactivación / confirmación
        if getattr(self, "is_completed", False):
            pose_pts = landmarks.pose if hasattr(landmarks, "pose") else landmarks
            if pose_pts is not None and len(pose_pts) > 16:
                sh_line = (pose_pts[11].y + pose_pts[12].y) / 2.0
                hands_up = (pose_pts[15].y < sh_line) or (pose_pts[16].y < sh_line)
                if hands_up and not self.finish_acknowledged:
                    self.finish_acknowledged = True
                    self.event_bus.publish(AppEvent.REP_COMPLETED, {
                        "reps": 1,
                        "combo": self.combo,
                        "evaluation": "👍 ¡Gesto detectado! Pausa activa finalizada con éxito. ¡Buen trabajo!"
                    })

            avatar_img = CoachAvatar.render_pose("GESTO_PULGAR", self.tick, size=(190, 190))
            fb_text = "👍 ¡Pausa concluida! Pulsa 'Reiniciar Rutina' cuando gustes." if self.finish_acknowledged else "👍 Levanta el pulgar o tu mano para confirmar y desactivar la pausa"
            return {
                "pose_id": "FINALIZACION_GESTO",
                "type": "completed",
                "title": "¡Rutina Completada! 🎉",
                "subtitle": "Salud postural garantizada",
                "instruction": "Haz el gesto de pulgar arriba 👍 o levanta la mano para desactivar.",
                "is_matched": True,
                "is_completed": True,
                "progress_pct": 100,
                "progress_ratio": 1.0,
                "elapsed_sec": 0,
                "total_sec": 0,
                "score": self.score,
                "combo": self.combo,
                "streak_badge": f"🏆 ¡RUTINA COMPLETADA! ({self.score} pts)",
                "step_str": "Desactivar Pausa",
                "avatar_img": avatar_img,
                "has_video_guide": False,
                "hand_highlight": None,
                "hip_guide_pts": None,
                "shoulder_guide_pts": None,
                "chest_expansion_pct": 0.0,
                "shoulder_hiking": False,
                "warning_msg": None,
                "calf_reps": 10,
                "target_reps": 10,
                "tick": self.tick,
                "feedback": fb_text
            }

        # Estado 0: Saludo de Inicio Touchless (Levantar la mano / Saludar 👋 para comenzar)
        if getattr(self, "waiting_for_greeting", True):
            avatar_img = CoachAvatar.render_pose("SALUDO", self.tick, size=(190, 190))
            posture_info = detect_user_posture(landmarks)

            pose_pts = landmarks.pose if hasattr(landmarks, "pose") else landmarks
            if pose_pts is not None and len(pose_pts) > 16:
                sh_line = (pose_pts[11].y + pose_pts[12].y) / 2.0
                if (pose_pts[15].y < sh_line) or (pose_pts[16].y < sh_line):
                    self.waiting_for_greeting = False
                    self.event_bus.publish(AppEvent.REP_COMPLETED, {
                        "reps": 1,
                        "combo": 0,
                        "evaluation": "👋 ¡Hola! Saludo recibido. ¡Iniciando primer ejercicio ergonómico!"
                    })

            return {
                "pose_id": "SALUDO_INICIO",
                "type": "greeting",
                "title": "Saludo de Inicio 👋",
                "subtitle": "Activación Touchless",
                "instruction": "Levanta tu mano y saluda a tu Coach para comenzar sin tocar el ratón.",
                "is_matched": False,
                "is_completed": False,
                "progress_pct": 0,
                "progress_ratio": 0.0,
                "elapsed_sec": 0,
                "total_sec": 1.0,
                "score": self.score,
                "combo": self.combo,
                "streak_badge": "👋 SALUDA PARA INICIAR",
                "step_str": "Inicio Touchless",
                "avatar_img": avatar_img,
                "has_video_guide": False,
                "hand_highlight": None,
                "hip_guide_pts": None,
                "shoulder_guide_pts": None,
                "chest_expansion_pct": 0.0,
                "shoulder_hiking": False,
                "warning_msg": None,
                "calf_reps": 0,
                "target_reps": 10,
                "tick": self.tick,
                "feedback": "👋 Levanta tu mano frente a la cámara para iniciar la sesión",
                "user_posture": posture_info.get("label", "Buscando postura..."),
                "user_posture_icon": posture_info.get("icon", "👤"),
                "is_standing": posture_info.get("is_standing", False)
            }

        step_info = self.exercises[self.current_step_index % len(self.exercises)]
        ex_type = step_info.get("type", "wrist_stretch")
        step_id = step_info.get("id", "ESTIRAMIENTO_MUNECA")

        is_matched = False
        hand_highlight = None
        hip_guide_pts = None
        shoulder_guide_pts = None
        self.shoulder_hiking = False
        warning_msg = None
        detected_side = None

        posture_info = detect_user_posture(landmarks)
        pose_pts = None
        hands = []
        nose = ear_l = ear_r = sh_l = sh_r = el_l = el_r = w_l = w_r = hip_l = hip_r = None
        shoulder_line_y = 0.5

        if landmarks is not None:
            hands = landmarks.hands if hasattr(landmarks, "hands") else []
            pose_pts = landmarks.pose if hasattr(landmarks, "pose") else landmarks

            if pose_pts is not None and len(pose_pts) > 24:
                nose = pose_pts[0]
                ear_l, ear_r = pose_pts[7], pose_pts[8]
                sh_l, sh_r = pose_pts[11], pose_pts[12]
                el_l, el_r = pose_pts[13], pose_pts[14]
                w_l, w_r = pose_pts[15], pose_pts[16]
                hip_l, hip_r = pose_pts[23], pose_pts[24]
                shoulder_line_y = (sh_l.y + sh_r.y) / 2.0
            else:
                nose = ear_l = ear_r = sh_l = sh_r = el_l = el_r = w_l = w_r = hip_l = hip_r = None
                shoulder_line_y = 0.5

            # -------------------------------------------------------------
            # 1. ESTIRAMIENTO DE MUÑECAS (TÚNEL CARPIANO - BILATERAL)
            # Requiere estirar mano 1 por 5s, luego mano 2 por 5s
            # -------------------------------------------------------------
            if ex_type in ["wrist_stretch", "hand_right", "hand_left"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    angle_left = calculate_angle_2d((sh_l.x, sh_l.y), (el_l.x, el_l.y), (w_l.x, w_l.y))
                    angle_right = calculate_angle_2d((sh_r.x, sh_r.y), (el_r.x, el_r.y), (w_r.x, w_r.y))
                    dist_wrists = math.hypot(w_l.x - w_r.x, w_l.y - w_r.y)

                    left_elevated = (w_l.y < shoulder_line_y + 0.20) and (w_l.y > (nose.y - 0.10) if nose else (shoulder_line_y - 0.20))
                    right_elevated = (w_r.y < shoulder_line_y + 0.20) and (w_r.y > (nose.y - 0.10) if nose else (shoulder_line_y - 0.20))

                    left_2d_ext = (angle_left >= 130.0) and left_elevated
                    right_2d_ext = (angle_right >= 130.0) and right_elevated

                    sh_l_z = getattr(sh_l, "z", 0.0) or 0.0
                    w_l_z = getattr(w_l, "z", 0.0) or 0.0
                    sh_r_z = getattr(sh_r, "z", 0.0) or 0.0
                    w_r_z = getattr(w_r, "z", 0.0) or 0.0

                    left_forward_3d = ((sh_l_z - w_l_z) > 0.08) and left_elevated
                    right_forward_3d = ((sh_r_z - w_r_z) > 0.08) and right_elevated

                    left_active = left_2d_ext or left_forward_3d
                    right_active = right_2d_ext or right_forward_3d

                    # Detección de mano dedicada si está presente
                    if len(hands) >= 1:
                        hand_item = hands[0]
                        if hand_item[0].y < shoulder_line_y + 0.22 and hand_item[12].y < hand_item[0].y - 0.04:
                            if hand_item[0].x < 0.5:
                                right_active = True # Efecto espejo: lado derecho de la pantalla
                            else:
                                left_active = True

                    if left_active and not right_active:
                        detected_side = "LEFT"
                    elif right_active and not left_active:
                        detected_side = "RIGHT"
                    elif left_active and right_active:
                        detected_side = "LEFT" if self.current_side_phase == 1 else "RIGHT"

                    if detected_side:
                        target_w = w_l if detected_side == "LEFT" else w_r
                        hand_highlight = (int(target_w.x * frame_w), int(target_w.y * frame_h))

                    # Lógica bilateral: En fase 1 se acepta cualquier mano; en fase 2 se exige la contraria
                    if self.current_side_phase == 1:
                        if detected_side is not None:
                            is_matched = True
                        else:
                            warning_msg = "👉 Extiende un brazo al frente y jala suavemente los dedos (Mano 1/2)"
                    else: # Fase 2
                        expected = "RIGHT" if self.side_1_detected == "LEFT" else "LEFT"
                        if detected_side == expected:
                            is_matched = True
                        elif detected_side == self.side_1_detected:
                            warning_msg = f"🔄 ¡Ahora cambia! Estira la OTRA mano ({'Derecha' if expected == 'RIGHT' else 'Izquierda'} 2/2)"
                        else:
                            warning_msg = f"👉 Extiende la otra mano al frente ({'Derecha' if expected == 'RIGHT' else 'Izquierda'} 2/2)"

            # -------------------------------------------------------------
            # 2. ROTACIÓN Y CÍRCULOS DE HOMBROS (DESCARGA DE TRAPECIOS)
            # Exige encogimiento y movimiento real de hombros (cero falsos positivos)
            # -------------------------------------------------------------
            elif ex_type in ["shoulder_roll"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    hands_down = (w_l.y > shoulder_line_y + 0.12) and (w_r.y > shoulder_line_y + 0.12)
                    sh_y = (sh_l.y + sh_r.y) / 2.0

                    if self.shoulder_neutral_y is None:
                        self.shoulder_neutral_y = sh_y
                    else:
                        # Adaptación muy lenta al nivel de reposo
                        self.shoulder_neutral_y = 0.995 * self.shoulder_neutral_y + 0.005 * sh_y

                    # Hombros encogidos hacia arriba significativamente
                    sh_shrug = (self.shoulder_neutral_y - sh_y) > 0.024
                    ear_dist_l = abs(sh_l.y - ear_l.y) if ear_l else 0.25
                    ear_dist_r = abs(sh_r.y - ear_r.y) if ear_r else 0.25
                    close_to_ears = (ear_dist_l < 0.13) or (ear_dist_r < 0.13)

                    if hands_down and (sh_shrug or close_to_ears):
                        is_matched = True
                    elif not hands_down:
                        warning_msg = "👐 Mantén los brazos descansando abajo a los lados"
                    else:
                        warning_msg = "🔄 Eleva los hombros hacia las orejas y rótalos hacia atrás"

            # -------------------------------------------------------------
            # 3. APERTURA DE PECHO Y RETRACCIÓN ESCAPULAR (ANTI-JOROBA)
            # Exige postura en 'W': codos a la altura de hombros y antebrazos hacia arriba
            # -------------------------------------------------------------
            elif ex_type in ["chest_open", "zen_breath"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    sh_dist = abs(sh_l.x - sh_r.x)
                    elbow_dist = abs(el_l.x - el_r.x)
                    ratio = elbow_dist / max(0.01, sh_dist)

                    # Codos a la altura del hombro
                    elbows_elevated = (abs(el_l.y - sh_l.y) < 0.14) and (abs(el_r.y - sh_r.y) < 0.14)
                    # Codos bien separados hacia los lados
                    elbows_wide = ratio >= 1.28
                    # Manos y antebrazos apuntando HACIA ARRIBA (no caídos ni en el teclado)
                    hands_up = (w_l.y < el_l.y - 0.03) and (w_r.y < el_r.y - 0.03)

                    self.chest_expansion_pct = min(1.0, max(0.0, (ratio - 1.0) / 0.40))

                    if elbows_elevated and elbows_wide and hands_up:
                        is_matched = True
                    elif not hands_up:
                        warning_msg = "🙌 Eleva los antebrazos y manos hacia arriba (Postura en 'W')"
                    elif not elbows_elevated:
                        warning_msg = "💪 Eleva ambos codos a la altura de tus hombros"
                    elif not elbows_wide:
                        warning_msg = "🦅 Abre los codos hacia atrás juntando las escápulas"

            # -------------------------------------------------------------
            # 4. INCLINACIÓN LATERAL DE CUELLO (BILATERAL: Ambos lados obligatorios)
            # -------------------------------------------------------------
            elif ex_type in ["neck_tilt", "neck_stretch"]:
                if pose_pts is not None and len(pose_pts) > 12:
                    ear_angle = calculate_slope_angle((ear_l.x, ear_l.y), (ear_r.x, ear_r.y))
                    sh_angle = calculate_slope_angle((sh_l.x, sh_l.y), (sh_r.x, sh_r.y))
                    tilt_angle = abs(ear_angle - sh_angle)
                    ear_diff = abs(ear_l.y - ear_r.y)
                    shoulder_diff = abs(sh_l.y - sh_r.y)
                    hands_down = (w_l.y > shoulder_line_y + 0.05) and (w_r.y > shoulder_line_y + 0.05)

                    left_tilted = (ear_r.y > ear_l.y + 0.030) and (tilt_angle >= 11.5)
                    right_tilted = (ear_l.y > ear_r.y + 0.030) and (tilt_angle >= 11.5)

                    if left_tilted and not right_tilted:
                        detected_side = "LEFT"
                    elif right_tilted and not left_tilted:
                        detected_side = "RIGHT"

                    if shoulder_diff > 0.065:
                        self.shoulder_hiking = True
                        warning_msg = "⚠️ Baja el hombro, mantenlo relajado abajo"
                    elif self.current_side_phase == 1:
                        if detected_side is not None and hands_down:
                            is_matched = True
                        else:
                            warning_msg = "💆 Inclina suavemente la cabeza hacia un hombro (Lado 1/2)"
                    else: # Fase 2
                        expected = "RIGHT" if self.side_1_detected == "LEFT" else "LEFT"
                        if detected_side == expected and hands_down:
                            is_matched = True
                        elif detected_side == self.side_1_detected:
                            warning_msg = f"🔄 ¡Ahora al otro hombro! Inclina hacia el lado {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} (2/2)"
                        else:
                            warning_msg = f"💆 Inclina la cabeza hacia el hombro {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} (2/2)"

            # -------------------------------------------------------------
            # 5. ESTIRAMIENTO DE TRÍCEPS (BILATERAL: Ambos codos obligatorios)
            # -------------------------------------------------------------
            elif ex_type in ["triceps_stretch"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    # Un codo debe estar claramente elevado por encima del nivel del hombro
                    left_elevated = el_l.y < (shoulder_line_y - 0.04)
                    right_elevated = el_r.y < (shoulder_line_y - 0.04)

                    # Si el usuario sostiene el codo con la otra mano, el codo doblado más alto es el dominante
                    if left_elevated and (el_l.y < el_r.y - 0.03):
                        detected_side = "LEFT"
                    elif right_elevated and (el_r.y < el_l.y - 0.03):
                        detected_side = "RIGHT"
                    elif left_elevated and not right_elevated:
                        detected_side = "LEFT"
                    elif right_elevated and not left_elevated:
                        detected_side = "RIGHT"
                    elif left_elevated and right_elevated:
                        # Si ambos están arriba, el codo más flexionado o cuya mano esté tras la cabeza es el principal
                        dist_w_l = math.hypot(w_l.x - (nose.x if nose else 0.5), w_l.y - (nose.y if nose else 0.3))
                        dist_w_r = math.hypot(w_r.x - (nose.x if nose else 0.5), w_r.y - (nose.y if nose else 0.3))
                        detected_side = "LEFT" if dist_w_l < dist_w_r else "RIGHT"

                    if detected_side:
                        high_el = el_l if detected_side == "LEFT" else el_r
                        hand_highlight = (int(high_el.x * frame_w), int(high_el.y * frame_h))

                    if self.current_side_phase == 1:
                        if detected_side is not None:
                            is_matched = True
                        else:
                            warning_msg = "💪 Eleva un codo doblado tras tu cabeza (Brazo 1/2)"
                    else: # Fase 2
                        expected = "RIGHT" if self.side_1_detected == "LEFT" else "LEFT"
                        if detected_side == expected:
                            is_matched = True
                        elif detected_side == self.side_1_detected:
                            warning_msg = f"🔄 ¡Ahora cambia de brazo! Eleva el codo {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} (2/2)"
                        else:
                            warning_msg = f"💪 Eleva el codo {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} tras la cabeza (2/2)"

            # -------------------------------------------------------------
            # 6. TORSIÓN DE TRONCO (BILATERAL: Ambos lados de giro obligatorios)
            # -------------------------------------------------------------
            elif ex_type in ["trunk_twist"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    d_l = abs(nose.x - ear_l.x) if nose and ear_l else 0.1
                    d_r = abs(nose.x - ear_r.x) if nose and ear_r else 0.1
                    turn_ratio = d_l / max(0.005, d_r)
                    sh_center = (sh_l.x + sh_r.x) / 2.0
                    nose_displacement = abs(nose.x - sh_center) / max(0.01, abs(sh_l.x - sh_r.x)) if nose else 0

                    left_turned = (turn_ratio < 0.42) and (nose_displacement > 0.14)
                    right_turned = (turn_ratio > 2.38) and (nose_displacement > 0.14)

                    if left_turned and not right_turned:
                        detected_side = "LEFT"
                    elif right_turned and not left_turned:
                        detected_side = "RIGHT"

                    if self.current_side_phase == 1:
                        if detected_side is not None:
                            is_matched = True
                        else:
                            warning_msg = "🔄 Gira el torso suavemente hacia un lado mirando sobre tu hombro (Lado 1/2)"
                    else: # Fase 2
                        expected = "RIGHT" if self.side_1_detected == "LEFT" else "LEFT"
                        if detected_side == expected:
                            is_matched = True
                        elif detected_side == self.side_1_detected:
                            warning_msg = f"🔄 ¡Ahora gira hacia el otro lado! Rota al lado {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} (2/2)"
                        else:
                            warning_msg = f"🔄 Rota el torso hacia el lado {'Derecho' if expected == 'RIGHT' else 'Izquierdo'} (2/2)"

            # -------------------------------------------------------------
            # 7. BRAZOS AL CIELO (ELONGACIÓN AXIAL DE COLUMNA)
            # -------------------------------------------------------------
            elif ex_type in ["arms_up"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    arms_high = (w_l.y < nose.y - 0.05) and (w_r.y < nose.y - 0.05) if nose else ((w_l.y < shoulder_line_y - 0.20) and (w_r.y < shoulder_line_y - 0.20))
                    if arms_high:
                        is_matched = True
                    else:
                        warning_msg = "⬆ Eleva ambos brazos bien alto hacia el techo"

            # -------------------------------------------------------------
            # 8. BOMBEO DE PANTORRILLAS (ACTIVACIÓN CIRCULATORIA)
            # -------------------------------------------------------------
            elif ex_type in ["calf_raises", "squat"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    ref_y = (sh_l.y + sh_r.y) / 2.0
                    if self.calf_baseline_y is None:
                        self.calf_baseline_y = ref_y
                    else:
                        self.calf_baseline_y = 0.96 * self.calf_baseline_y + 0.04 * ref_y

                    elevation = self.calf_baseline_y - ref_y
                    now_rep = time.time()
                    last_rep = getattr(self, "last_rep_time", 0.0)

                    if elevation > 0.020 and self.calf_stage == "DOWN":
                        self.calf_stage = "UP"
                        is_matched = True
                    elif elevation < 0.008 and self.calf_stage == "UP":
                        if (now_rep - last_rep) > 0.35:
                            self.calf_stage = "DOWN"
                            self.calf_reps += 1
                            self.last_rep_time = now_rep
                            is_matched = True
                            self.event_bus.publish(AppEvent.REP_COMPLETED, {
                                "reps": self.calf_reps,
                                "evaluation": f"Puntillas: {self.calf_reps}/10. Activación venosa de piernas."
                            })
                    elif self.calf_stage == "UP":
                        is_matched = True

                    if self.calf_reps >= step_info.get("target_reps", 10):
                        is_matched = True

        # ================= MANEJO DE TIEMPO SOSTENIDO Y TRANSICIÓN BILATERAL =================
        now = time.time()
        is_bilateral = ex_type in BILATERAL_TYPES
        total_hold = step_info.get("hold_sec", 8.0)
        phase_target = (total_hold / 2.0) if is_bilateral else total_hold

        elapsed = 0.0
        step_completed = False

        if is_matched:
            self.last_matched_time = now
            if self.hold_start_time is None:
                self.hold_start_time = now
            elapsed = now - self.hold_start_time
        else:
            last_match = getattr(self, "last_matched_time", 0.0)
            if self.hold_start_time is not None and (now - last_match) < 0.40:
                elapsed = last_match - self.hold_start_time
            else:
                self.hold_start_time = None
                elapsed = 0.0

        # Progreso numérico
        if ex_type == "calf_raises":
            target_r = step_info.get("target_reps", 10)
            progress_pct = min(1.0, self.calf_reps / float(target_r))
            step_completed = (self.calf_reps >= target_r)
        elif is_bilateral:
            current_phase_prog = min(1.0, elapsed / phase_target)
            if self.current_side_phase == 1:
                progress_pct = current_phase_prog * 0.50
                if elapsed >= phase_target:
                    # Completó Lado 1 -> Pasar a Lado 2
                    self.side_1_detected = detected_side or "LEFT"
                    self.current_side_phase = 2
                    self.hold_start_time = None
                    self.side_switch_time = now
                    self.event_bus.publish(AppEvent.REP_COMPLETED, {
                        "reps": 1,
                        "combo": self.combo,
                        "evaluation": f"¡Lado 1 listo! Ahora cambia y realiza el otro lado ({'Derecho' if self.side_1_detected == 'LEFT' else 'Izquierdo'})."
                    })
            else: # Fase 2
                progress_pct = 0.50 + (current_phase_prog * 0.50)
                if elapsed >= phase_target:
                    step_completed = True
        else:
            progress_pct = min(1.0, elapsed / total_hold)
            step_completed = is_matched and (elapsed >= total_hold)

        # Si el ejercicio terminó por completo:
        if step_completed:
            self.score += 150 + (self.combo * 25)
            self.combo += 1
            self.hold_start_time = None
            self.current_side_phase = 1
            self.side_1_detected = None
            self.calf_reps = 0
            self.calf_stage = "DOWN"

            self.event_bus.publish(AppEvent.REP_COMPLETED, {
                "reps": self.score // 100,
                "combo": self.combo,
                "evaluation": f"¡Excelente! Ejercicio '{step_info['title']}' completado con técnica perfecta."
            })

            if self.current_step_index >= len(self.exercises) - 1:
                self.is_completed = True
                self.completed_cycles += 1
                self.event_bus.publish(AppEvent.REP_COMPLETED, {
                    "reps": self.score // 100,
                    "combo": self.combo,
                    "evaluation": "🎉 ¡Rutina Ergonómica finalizada con éxito! Excelente trabajo."
                })
            else:
                self.current_step_index += 1

        # ================= COACH VIRTUAL STICKMAN ARTICULADO =================
        avatar_img = CoachAvatar.render_pose(step_id, self.tick, size=(190, 190))

        # Feedback dinámico y específico por ejercicio y lado
        if warning_msg:
            fb = warning_msg
        elif is_matched:
            side_str = f"({'Lado 1/2' if self.current_side_phase == 1 else 'Lado 2/2'})" if is_bilateral else ""
            if ex_type in ["wrist_stretch", "hand_right", "hand_left"]:
                fb = f"✨ ¡Excelente! Mantén la muñeca estirada liberando el túnel carpiano {side_str}"
            elif ex_type in ["shoulder_roll"]:
                fb = "✨ ¡Excelente rotación! Descargando trapecios y cuello"
            elif ex_type in ["chest_open", "zen_breath"]:
                fb = "✨ ¡Gran apertura en 'W'! Escápulas juntas liberando hombros"
            elif ex_type in ["neck_tilt", "neck_stretch"]:
                fb = f"✨ ¡Muy bien! Mantén el cuello relajado {side_str}"
            elif ex_type in ["triceps_stretch"]:
                fb = f"✨ ¡Gran estiramiento de tríceps! {side_str}"
            elif ex_type == "trunk_twist":
                fb = f"✨ ¡Buena torsión lumbar! {side_str}"
            elif ex_type in ["arms_up"]:
                fb = "✨ ¡Excelente elongación! Alargando vértebras y columna"
            elif ex_type == "calf_raises":
                fb = f"🦵 ¡Muy bien! Repetición {self.calf_reps}/10 en puntillas"
            else:
                fb = "¡PERFECTO! MANTÉN LA POSTURA"
        else:
            fb = step_info.get("desc", "Sigue la guía visual del Coach")

        if self.combo >= 6:
            streak_badge = f"🔥 COMBO x{self.combo} (¡ERGONOMÍA TOTAL!)"
        elif self.combo >= 3:
            streak_badge = f"⭐ COMBO x{self.combo}"
        else:
            streak_badge = f"COMBO x{self.combo}"

        # Flecha direccional guía para ejercicios bilaterales (Lado 1 y Lado 2)
        guide_direction = None
        guide_center_pt = None
        if is_bilateral and not getattr(self, "is_completed", False):
            if self.current_side_phase == 1:
                guide_direction = "LEFT"
            else:
                guide_direction = "RIGHT" if self.side_1_detected == "LEFT" else "LEFT"

            if pose_pts is not None and len(pose_pts) > 16:
                if ex_type in ["neck_tilt", "neck_stretch"]:
                    guide_center_pt = (int(nose.x * frame_w), int(nose.y * frame_h)) if nose else None
                elif ex_type in ["triceps_stretch"]:
                    guide_center_pt = (int(nose.x * frame_w), int((shoulder_line_y - 0.06) * frame_h)) if nose else None
                elif ex_type in ["trunk_twist"]:
                    guide_center_pt = (int(nose.x * frame_w), int(shoulder_line_y * frame_h)) if nose else None
                elif ex_type in ["wrist_stretch", "hand_right", "hand_left"]:
                    target_ref = sh_l if guide_direction == "LEFT" else sh_r
                    guide_center_pt = (int(target_ref.x * frame_w), int((shoulder_line_y + 0.04) * frame_h)) if target_ref else None

        # Cadena de paso con indicación de lado si aplica
        base_step_str = f"Paso {self.current_step_index + 1}/{len(self.exercises)}: {step_info['title']}"
        if is_bilateral:
            base_step_str += f" [Lado {self.current_side_phase}/2]"

        return {
            "pose_id": step_id,
            "type": ex_type,
            "title": step_info["title"],
            "subtitle": step_info.get("subtitle", "Pausa Ergonómica"),
            "instruction": step_info.get("desc", "Sigue la guía visual del Coach"),
            "is_matched": is_matched,
            "is_completed": getattr(self, "is_completed", False),
            "progress_pct": int(progress_pct * 100),
            "progress_ratio": progress_pct,
            "elapsed_sec": elapsed,
            "total_sec": total_hold,
            "score": self.score,
            "combo": self.combo,
            "streak_badge": streak_badge,
            "step_str": base_step_str,
            "avatar_img": avatar_img,
            "has_video_guide": False,
            "hand_highlight": hand_highlight,
            "guide_direction": guide_direction,
            "guide_center_pt": guide_center_pt,
            "hip_guide_pts": hip_guide_pts,
            "shoulder_guide_pts": shoulder_guide_pts,
            "chest_expansion_pct": self.chest_expansion_pct,
            "shoulder_hiking": self.shoulder_hiking,
            "warning_msg": warning_msg,
            "calf_reps": self.calf_reps,
            "target_reps": step_info.get("target_reps", 10),
            "tick": self.tick,
            "feedback": fb,
            "user_posture": posture_info.get("label", "Buscando postura..."),
            "user_posture_icon": posture_info.get("icon", "👤"),
            "is_standing": posture_info.get("is_standing", False)
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "puntos_obtenidos": self.score,
            "combo_maximo": self.combo,
            "ciclos_completados": self.completed_cycles,
            "beneficio_alcanzado": "Reducción de estrés biomecánico, protección de túnel carpiano y descarga dorsal/lumbar."
        }
