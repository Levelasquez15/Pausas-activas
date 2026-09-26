"""
Estrategia Gamificada de Pausas Activas (TuxDance: Pausas Activas Ergonómicas).
Soporta los 5 ejercicios ergonómicos oficiales (Muñecas, Apertura de Pecho, Cuello,
Torsión de Tronco y Bombeo de Pantorrillas).
Integra reproducción automática de videos y audio (.mp4 en `assets/videos/`)
con fallback automático al Coach Virtual animado.
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

        # Estados específicos para ejercicios
        self.calf_reps = 0
        self.calf_stage = "DOWN"
        self.calf_baseline_y = None
        self.shoulder_hiking = False
        self.chest_expansion_pct = 0.0

    def reload_exercises(self):
        """Recarga la lista de ejercicios si el usuario agregó o editó alguno."""
        self.exercises = self.exercise_manager.get_all()
        if self.current_step_index >= len(self.exercises):
            self.current_step_index = 0

    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        self.tick += 1
        h, w = frame_shape[:2]
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

        posture_info = detect_user_posture(landmarks)

        if landmarks is not None:
            # Extraer manos dedicadas si están disponibles
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
            # 1. ESTIRAMIENTO DE MUÑECAS (TÚNEL CARPIANO)
            # Requiere extensión deliberada de brazo al frente a altura del pecho/hombro
            # -------------------------------------------------------------
            if ex_type in ["wrist_stretch", "hand_right", "hand_left"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    angle_left = calculate_angle_2d((sh_l.x, sh_l.y), (el_l.x, el_l.y), (w_l.x, w_l.y))
                    angle_right = calculate_angle_2d((sh_r.x, sh_r.y), (el_r.x, el_r.y), (w_r.x, w_r.y))
                    dist_wrists = math.hypot(w_l.x - w_r.x, w_l.y - w_r.y)

                    # Altura activa de muñecas (área entre pecho y hombros, por encima del escritorio/regazo)
                    left_elevated = (w_l.y < shoulder_line_y + 0.28) and (w_l.y > (nose.y - 0.08) if nose else (shoulder_line_y - 0.20)) and (w_l.y < 0.75)
                    right_elevated = (w_r.y < shoulder_line_y + 0.28) and (w_r.y > (nose.y - 0.08) if nose else (shoulder_line_y - 0.20)) and (w_r.y < 0.75)

                    # 1. Extensión 2D (cuando se hace de lado o en ángulo de 45°)
                    left_2d_ext = (angle_left >= 125.0) and left_elevated
                    right_2d_ext = (angle_right >= 125.0) and right_elevated

                    # 2. Extensión 3D hacia la cámara (DE FRENTE):
                    # En MediaPipe, el eje Z es negativo hacia la lente de la cámara
                    sh_l_z = getattr(sh_l, "z", 0.0) or 0.0
                    w_l_z = getattr(w_l, "z", 0.0) or 0.0
                    sh_r_z = getattr(sh_r, "z", 0.0) or 0.0
                    w_r_z = getattr(w_r, "z", 0.0) or 0.0

                    left_forward_3d = ((sh_l_z - w_l_z) > 0.06) and left_elevated
                    right_forward_3d = ((sh_r_z - w_r_z) > 0.06) and right_elevated

                    arm_extended = left_2d_ext or right_2d_ext or left_forward_3d or right_forward_3d

                    # 3. Asistencia bimanual frente al pecho (ambas manos juntas estirando dedos de frente)
                    both_wrists_elevated = left_elevated and right_elevated
                    bimanual_pose = both_wrists_elevated and (dist_wrists < 0.25)

                    bimanual_hands = False
                    if len(hands) >= 2:
                        h1, h2 = hands[0], hands[1]
                        dist_h = math.hypot(h1[9].x - h2[9].x, h1[9].y - h2[9].y)
                        hands_up = (h1[0].y < shoulder_line_y + 0.28) and (h2[0].y < shoulder_line_y + 0.28)
                        if dist_h < 0.30 and hands_up:
                            bimanual_hands = True

                    # 4. Mano individual abierta frente a la cámara (dedos extendidos arriba)
                    single_hand_forward = False
                    if len(hands) == 1 and (arm_extended or left_elevated or right_elevated):
                        h = hands[0]
                        if h[0].y < shoulder_line_y + 0.28:
                            if h[12].y < h[0].y - 0.03: # Dedos apuntando arriba
                                single_hand_forward = True

                    if bimanual_hands or bimanual_pose:
                        is_matched = True
                        target_w = w_l if left_elevated else w_r
                        hand_highlight = (int(target_w.x * w), int(target_w.y * h))
                    elif arm_extended or single_hand_forward:
                        is_matched = True
                        target_w = w_l if (left_2d_ext or left_forward_3d or left_elevated) else w_r
                        hand_highlight = (int(target_w.x * w), int(target_w.y * h))
                    else:
                        warning_msg = "👉 Extiende el brazo al frente y jala suavemente los dedos hacia ti"

            # -------------------------------------------------------------
            # 2. APERTURA DE PECHO Y RETRACCIÓN ESCAPULAR (ANTI-JOROBA)
            # Requiere postura en 'W' / cactus: codos elevados al nivel del hombro y separados
            # -------------------------------------------------------------
            elif ex_type in ["chest_open", "zen_breath"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    sh_dist = abs(sh_l.x - sh_r.x)
                    elbow_dist = abs(el_l.x - el_r.x)
                    ratio = elbow_dist / max(0.01, sh_dist)

                    # Los codos NO deben estar caídos sobre los reposabrazos o cintura
                    elbows_elevated = (abs(el_l.y - sh_l.y) < 0.22) and (abs(el_r.y - sh_r.y) < 0.22)
                    # Manos no deben estar colgadas hacia abajo
                    hands_up = (w_l.y <= el_l.y + 0.12) and (w_r.y <= el_r.y + 0.12)
                    # Codos abiertos hacia los lados (postura W)
                    elbows_wide = ratio >= 1.25

                    self.chest_expansion_pct = min(1.0, max(0.0, (ratio - 1.0) / 0.40))

                    if elbows_elevated and elbows_wide and hands_up:
                        is_matched = True
                    elif not elbows_elevated:
                        warning_msg = "💪 Eleva ambos codos a la altura de tus hombros"
                    elif not elbows_wide:
                        warning_msg = "🦅 Abre los codos hacia atrás en forma de 'W' abriendo el pecho"
                    elif not hands_up:
                        warning_msg = "🙌 Mantén las palmas y antebrazos hacia arriba"

            # -------------------------------------------------------------
            # 3. INCLINACIÓN LATERAL DE CUELLO (LIBERACIÓN CERVICAL)
            # Requiere inclinación real de orejas sin subir el hombro
            # -------------------------------------------------------------
            elif ex_type in ["neck_tilt", "neck_stretch"]:
                if pose_pts is not None and len(pose_pts) > 12:
                    ear_angle = calculate_slope_angle((ear_l.x, ear_l.y), (ear_r.x, ear_r.y))
                    sh_angle = calculate_slope_angle((sh_l.x, sh_l.y), (sh_r.x, sh_r.y))
                    tilt_angle = abs(ear_angle - sh_angle)
                    ear_diff = abs(ear_l.y - ear_r.y)
                    shoulder_diff = abs(sh_l.y - sh_r.y)

                    hands_down = (w_l.y > shoulder_line_y - 0.05) and (w_r.y > shoulder_line_y - 0.05)

                    if shoulder_diff > 0.065:
                        self.shoulder_hiking = True
                        warning_msg = "⚠️ Baja el hombro, mantenlo relajado"
                    elif tilt_angle >= 12.0 and ear_diff >= 0.032 and hands_down:
                        is_matched = True
                    else:
                        warning_msg = "💆 Inclina suavemente la cabeza hacia un hombro (oreja al hombro)"

            # -------------------------------------------------------------
            # 4. TORSIÓN DE TRONCO (DESCARGA LUMBAR)
            # Requiere rotación de cabeza y torso mirando hacia el costado
            # -------------------------------------------------------------
            elif ex_type in ["trunk_twist"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    d_l = abs(nose.x - ear_l.x) if nose and ear_l else 0.1
                    d_r = abs(nose.x - ear_r.x) if nose and ear_r else 0.1
                    turn_ratio = d_l / max(0.005, d_r)

                    # Cabeza rotada lateralmente sobre el hombro
                    head_turned = (turn_ratio < 0.42) or (turn_ratio > 2.38)

                    # Desplazamiento del eje del pecho / nariz
                    sh_center = (sh_l.x + sh_r.x) / 2.0
                    nose_displacement = abs(nose.x - sh_center) / max(0.01, abs(sh_l.x - sh_r.x)) if nose else 0

                    if head_turned and (nose_displacement > 0.14):
                        is_matched = True
                    else:
                        warning_msg = "🔄 Gira el torso suavemente hacia un lado mirando sobre tu hombro"

            # -------------------------------------------------------------
            # 5. BOMBEO DE PANTORRILLAS (ACTIVACIÓN CIRCULATORIA)
            # Conteo de 10 elevaciones rítmicas con debounce estricto
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

                    if elevation > 0.018 and self.calf_stage == "DOWN":
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

            # -------------------------------------------------------------
            # 6. ROTACIÓN Y CÍRCULOS DE HOMBROS (DESCARGA DE TRAPECIOS)
            # -------------------------------------------------------------
            elif ex_type in ["shoulder_roll"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    hands_down = (w_l.y > shoulder_line_y - 0.05) and (w_r.y > shoulder_line_y - 0.05)
                    sh_y = (sh_l.y + sh_r.y) / 2.0
                    if not hasattr(self, "shoulder_neutral_y") or self.shoulder_neutral_y is None:
                        self.shoulder_neutral_y = sh_y
                    else:
                        self.shoulder_neutral_y = 0.98 * self.shoulder_neutral_y + 0.02 * sh_y

                    sh_movement = abs(sh_y - self.shoulder_neutral_y)
                    sh_elevated = (sh_y < self.shoulder_neutral_y - 0.010) or (sh_movement > 0.006)

                    if hands_down and sh_elevated:
                        is_matched = True
                    elif not hands_down:
                        warning_msg = "👐 Mantén los brazos y manos abajo relajados"
                    else:
                        warning_msg = "🔄 Rota los hombros en círculos amplios hacia atrás"

            # -------------------------------------------------------------
            # 7. ESTIRAMIENTO DE TRÍCEPS Y DORSALES (BRAZO SOBRE LA CABEZA)
            # -------------------------------------------------------------
            elif ex_type in ["triceps_stretch"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    left_high = el_l.y < (nose.y + 0.04) if nose else (el_l.y < shoulder_line_y - 0.15)
                    right_high = el_r.y < (nose.y + 0.04) if nose else (el_r.y < shoulder_line_y - 0.15)

                    if left_high or right_high:
                        high_el = el_l if left_high else el_r
                        is_matched = True
                        hand_highlight = (int(high_el.x * w), int(high_el.y * h))
                    else:
                        warning_msg = "💪 Eleva un codo doblado por encima de tu cabeza"

            # -------------------------------------------------------------
            # 8. EXTENSIÓN LUMBAR (MANOS A LA CINTURA Y TORSO ATRÁS)
            # -------------------------------------------------------------
            elif ex_type in ["lumbar_extension"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    hands_at_waist = (w_l.y > shoulder_line_y + 0.18) and (w_r.y > shoulder_line_y + 0.18)
                    elbows_back = abs(el_l.x - el_r.x) > (abs(sh_l.x - sh_r.x) * 1.08)

                    if hands_at_waist and elbows_back:
                        is_matched = True
                    elif not hands_at_waist:
                        warning_msg = "👐 Coloca ambas manos en la espalda baja o cintura"
                    else:
                        warning_msg = "📐 Lleva los codos hacia atrás y arquea suavemente el torso"

            # -------------------------------------------------------------
            # 9. BRAZOS AL CIELO (ELONGACIÓN AXIAL DE COLUMNA)
            # -------------------------------------------------------------
            elif ex_type in ["arms_up"]:
                if pose_pts is not None and len(pose_pts) > 16:
                    arms_high = (w_l.y < nose.y - 0.05) and (w_r.y < nose.y - 0.05) if nose else ((w_l.y < shoulder_line_y - 0.20) and (w_r.y < shoulder_line_y - 0.20))
                    if arms_high:
                        is_matched = True
                    else:
                        warning_msg = "⬆ Eleva ambos brazos bien alto hacia el techo"

        # ================= MANEJO DE TIEMPO SOSTENIDO CON BÚFER DE GRACIA =================
        now = time.time()
        hold_target = step_info.get("hold_sec", 6.0)
        progress_pct = 0.0
        elapsed = 0.0

        if is_matched:
            self.last_matched_time = now
            if self.hold_start_time is None:
                self.hold_start_time = now
            elapsed = now - self.hold_start_time
            progress_pct = min(1.0, elapsed / hold_target)
        else:
            # Si se interrumpe la postura, pausar brevemente sin borrar inmediatamente (0.4s)
            last_match = getattr(self, "last_matched_time", 0.0)
            if self.hold_start_time is not None and (now - last_match) < 0.40:
                elapsed = last_match - self.hold_start_time
                progress_pct = min(1.0, elapsed / hold_target)
            else:
                self.hold_start_time = None
                progress_pct = 0.0
                elapsed = 0.0

        # Para bombeo de pantorrillas, el avance se basa en las 10 repeticiones
        if ex_type == "calf_raises":
            target_r = step_info.get("target_reps", 10)
            progress_pct = min(1.0, self.calf_reps / float(target_r))
            step_completed = (self.calf_reps >= target_r)
        else:
            step_completed = is_matched and (elapsed >= hold_target)

        if step_completed:
            # ¡Paso ergonómico superado con éxito!
            self.score += 150 + (self.combo * 25)
            self.combo += 1
            self.hold_start_time = None
            self.calf_reps = 0
            self.calf_stage = "DOWN"

            self.event_bus.publish(AppEvent.REP_COMPLETED, {
                "reps": self.score // 100,
                "combo": self.combo,
                "evaluation": f"¡Excelente! Ejercicio '{step_info['title']}' completado con técnica perfecta."
            })

            # Si terminamos el último ejercicio, detener la rutina y celebrar
            if self.current_step_index >= len(self.exercises) - 1:
                self.is_completed = True
                self.completed_cycles += 1
                self.event_bus.publish(AppEvent.REP_COMPLETED, {
                    "reps": self.score // 100,
                    "combo": self.combo,
                    "evaluation": "🎉 ¡Rutina Ergonómica de Pausas Activas finalizada! Excelente trabajo."
                })
            else:
                self.current_step_index += 1

        # ================= COACH VIRTUAL STICKMAN ARTICULADO =================
        avatar_img = CoachAvatar.render_pose(step_id, self.tick, size=(190, 190))
        has_video_guide = False

        # Feedback dinámico y específico por ejercicio
        if warning_msg:
            fb = warning_msg
        elif is_matched:
            if ex_type in ["wrist_stretch", "hand_right", "hand_left"]:
                fb = "✨ ¡Excelente! Mantén la muñeca estirada liberando el túnel carpiano"
            elif ex_type in ["shoulder_roll"]:
                fb = "✨ ¡Excelente rotación! Descargando trapecios y cuello"
            elif ex_type in ["chest_open", "zen_breath"]:
                fb = "✨ ¡Gran apertura! Escápulas juntas descargando hombros y espalda alta"
            elif ex_type in ["neck_tilt", "neck_stretch"]:
                fb = "✨ ¡Muy bien! Mantén el cuello relajado estirando las cervicales"
            elif ex_type in ["triceps_stretch"]:
                fb = "✨ ¡Gran estiramiento! Descomprimiendo tríceps y dorsales"
            elif ex_type == "trunk_twist":
                fb = "✨ ¡Buena torsión lumbar! Mantén la columna erguida y respira con calma"
            elif ex_type in ["lumbar_extension"]:
                fb = "✨ ¡Muy bien! Descomprimiendo la columna lumbar y espalda baja"
            elif ex_type in ["arms_up"]:
                fb = "✨ ¡Excelente elongación! Alargando vértebras y columna"
            elif ex_type == "calf_raises":
                fb = f"🦵 ¡Muy bien! Repetición {self.calf_reps}/10 en puntillas"
            else:
                fb = "¡PERFECTO! MANTÉN LA POSTURA"
        else:
            fb = step_info.get("desc", "Sigue la guía visual del Coach")

        # Badge de combo
        if self.combo >= 6:
            streak_badge = f"🔥 COMBO x{self.combo} (¡ERGONOMÍA TOTAL!)"
        elif self.combo >= 3:
            streak_badge = f"⭐ COMBO x{self.combo}"
        else:
            streak_badge = f"COMBO x{self.combo}"

        return {
            "pose_id": step_id,
            "type": ex_type,
            "title": step_info["title"],
            "subtitle": step_info.get("subtitle", ""),
            "instruction": step_info.get("desc", ""),
            "is_matched": is_matched,
            "is_completed": getattr(self, "is_completed", False),
            "progress_pct": int(progress_pct * 100),
            "progress_ratio": progress_pct,
            "elapsed_sec": elapsed,
            "total_sec": hold_target,
            "score": self.score,
            "combo": self.combo,
            "streak_badge": streak_badge,
            "step_str": f"Paso {self.current_step_index + 1} de {len(self.exercises)}",
            "avatar_img": avatar_img,
            "has_video_guide": has_video_guide,
            "hand_highlight": hand_highlight,
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
            "rutina": self.name,
            "puntuacion": self.score,
            "combo_maximo": self.combo,
            "rondas_completadas": self.completed_cycles,
            "diagnostico_fisico": f"Completaste {self.completed_cycles} ciclos del Catálogo Ergonómico 5-en-1."
        }
