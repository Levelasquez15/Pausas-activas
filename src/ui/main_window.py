"""
Ventana Principal de la Aplicación de Pausas Activas.
Construida con CustomTkinter para una apariencia moderna, ergonómica y profesional.
Arquitectura de 3 Columnas:
1. Barra Lateral (Navegación, Rutinas, Temporizador de Pausas)
2. Visor Central de Cámara (Amplio, Limpio y sin saturación visual)
3. Panel Lateral Derecho (Coach Stickman, Postura Sentado/De Pie, Instrucciones a Detalle, Contador)
"""
import time
import threading
import cv2
import numpy as np
from PIL import Image
import customtkinter as ctk

from src.config import AppConfig
from src.patterns.observer import EventBus, AppEvent
from src.patterns.state import StateManager, AppState
from src.vision.pose_detector import PoseDetectorFactory
from src.strategies.squat_strategy import SquatStrategy
from src.strategies.breathing_strategy import BreathingStrategy
from src.strategies.stretch_strategy import StretchStrategy
from src.strategies.dance_game_strategy import DanceGameStrategy
from src.audio.sound_manager import SoundManager
from src.storage.history_db import HistoryDB
from src.ui.breathing_widget import BreathingCanvasWidget
from src.ui.coach_avatar import CoachAvatar
from src.ui.exercise_details import get_exercise_detail
from src.ui.draw_utils import draw_pill_text, draw_direction_indicator
from src.ui.exercise_editor_window import ExerciseEditorWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = AppConfig()
        self.title(self.config.WINDOW_TITLE)
        self.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        self.minsize(1150, 700)

        # Servicios e instancias
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.sound_manager = SoundManager()
        self.history_db = HistoryDB()

        # Detector de poses con MediaPipe
        try:
            self.pose_detector = PoseDetectorFactory.create_detector()
            self.detector_ready = True
        except Exception as e:
            print(f"[Aviso] PoseDetector no disponible: {e}")
            self.pose_detector = None
            self.detector_ready = False

        # Estrategias ergonómicas
        self.dance_strategy = DanceGameStrategy(self.config)
        self.stretch_strategy = StretchStrategy(self.config)
        self.squat_strategy = SquatStrategy(self.config)
        self.breathing_triangle_strategy = BreathingStrategy(mode="triangular", config=self.config)
        self.breathing_478_strategy = BreathingStrategy(mode="478", config=self.config)

        # Estrategia seleccionada por defecto
        self.active_strategy = self.dance_strategy

        # Control de cámara y temporizador
        self.cap = None
        self.is_camera_running = False
        self.camera_thread = None

        # Temporizador de descanso de oficina (Pomodoro ergonómico)
        self.time_until_break_seconds = self.config.WORK_INTERVAL_MINUTES * 60
        self.is_break_active = False

        # Construir Interfaz Gráfica Moderna
        self._build_ui()
        self._subscribe_events()

        # Iniciar temporizador de escritorio en segundo plano
        self.after(1000, self._update_work_timer)

        # Inicializar panel derecho con el ejercicio activo
        self._update_right_panel_static_info()

        # Mostrar pantalla limpia de cámara en espera
        self._show_camera_standby()

        # Protocolo de cierre limpio de ventana
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):

        # 3 Columnas principales: [0] Sidebar (240px) | [1] Cámara Centro (Expandible) | [2] Panel Derecho (340px)
        # 3 Columnas principales: [0] Sidebar (250px) | [1] Cámara Centro (Expandible) | [2] Panel Derecho (340px)
        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=340)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # COLUMNA 1: BARRA LATERAL IZQUIERDA (NAVEGACIÓN & TEMPORIZADOR)
        # =====================================================================
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=self.config.COLOR_BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # Logotipo y encabezado estilo SaaS / Refero
        title_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_box.pack(fill="x", padx=16, pady=(18, 12))
        
        # Pill status badge sutil
        status_pill = ctk.CTkLabel(
            title_box,
            text="● IA ERGONOMÍA",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#10B981"
        )
        status_pill.pack(anchor="w", pady=(0, 2))

        lbl_app_logo = ctk.CTkLabel(
            title_box,
            text="Pausas Activas",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.config.COLOR_TEXT_MAIN
        )
        lbl_app_logo.pack(anchor="w")

        lbl_app_sub = ctk.CTkLabel(
            title_box,
            text="Salud Postural en el Trabajo",
            font=ctk.CTkFont(size=11),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        lbl_app_sub.pack(anchor="w")

        # Tarjeta Temporizador Pomodoro/Pausa (Refero Minimal Card)
        self.timer_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE
        )
        self.timer_card.pack(fill="x", padx=14, pady=8)

        timer_title = ctk.CTkLabel(
            self.timer_card,
            text="PRÓXIMA PAUSA EN",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        timer_title.pack(pady=(10, 2), padx=12, anchor="w")

        self.timer_display = ctk.CTkLabel(
            self.timer_card,
            text="45:00",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.config.COLOR_TEXT_MAIN
        )
        self.timer_display.pack(pady=(0, 6), padx=12, anchor="w")

        self.btn_trigger_break = ctk.CTkButton(
            self.timer_card,
            text="Hacer Pausa Ahora",
            command=self._manual_start_break,
            fg_color=self.config.COLOR_SURFACE_HOVER,
            hover_color="#223049",
            border_width=1,
            border_color=self.config.COLOR_BORDER_STRONG,
            text_color=self.config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            corner_radius=8
        )
        self.btn_trigger_break.pack(padx=12, pady=(0, 10), fill="x")

        # Separador / Categorías
        sep_lbl = ctk.CTkLabel(
            self.sidebar,
            text="CATÁLOGO DE RUTINAS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        sep_lbl.pack(pady=(14, 6), padx=16, anchor="w")

        # Botones de Rutina (Navegación minimalista estilo Linear/Refero)
        self.btn_dance = ctk.CTkButton(
            self.sidebar,
            text="🕺 Pausa Ergonómica 5-en-1",
            command=lambda: self._select_routine("dance"),
            fg_color=self.config.COLOR_SURFACE_HOVER,
            hover_color="#1e293b",
            border_width=1,
            border_color=self.config.COLOR_BORDER_STRONG,
            text_color=self.config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8,
            anchor="w"
        )
        self.btn_dance.pack(padx=12, pady=2, fill="x")

        self.btn_stretch = ctk.CTkButton(
            self.sidebar,
            text="🙆‍♂️ Estiramiento Cervical",
            command=lambda: self._select_routine("stretch"),
            fg_color="transparent",
            hover_color=self.config.COLOR_SURFACE_HOVER,
            border_width=0,
            text_color=self.config.COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8,
            anchor="w"
        )
        self.btn_stretch.pack(padx=12, pady=2, fill="x")

        self.btn_squat = ctk.CTkButton(
            self.sidebar,
            text="🏋️‍♂️ Sentadillas Activas",
            command=lambda: self._select_routine("squat"),
            fg_color="transparent",
            hover_color=self.config.COLOR_SURFACE_HOVER,
            border_width=0,
            text_color=self.config.COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8,
            anchor="w"
        )
        self.btn_squat.pack(padx=12, pady=2, fill="x")

        self.btn_breath_triangle = ctk.CTkButton(
            self.sidebar,
            text="🌬️ Respiración Triangular",
            command=lambda: self._select_routine("triangle"),
            fg_color="transparent",
            hover_color=self.config.COLOR_SURFACE_HOVER,
            border_width=0,
            text_color=self.config.COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8,
            anchor="w"
        )
        self.btn_breath_triangle.pack(padx=12, pady=2, fill="x")

        self.btn_breath_478 = ctk.CTkButton(
            self.sidebar,
            text="🧘 Técnica 4-7-8 (Calma)",
            command=lambda: self._select_routine("478"),
            fg_color="transparent",
            hover_color=self.config.COLOR_SURFACE_HOVER,
            border_width=0,
            text_color=self.config.COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8,
            anchor="w"
        )
        self.btn_breath_478.pack(padx=12, pady=2, fill="x")

        # Botón para Personalizar Ejercicios
        self.btn_edit_exercises = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Personalizar Ejercicios",
            command=self._open_exercise_editor,
            fg_color="transparent",
            hover_color=self.config.COLOR_SURFACE_HOVER,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            text_color=self.config.COLOR_TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            height=32,
            corner_radius=8
        )
        self.btn_edit_exercises.pack(padx=12, pady=(12, 4), fill="x")

        # Control de Cámara On/Off
        self.btn_cam_toggle = ctk.CTkButton(
            self.sidebar,
            text="📷 Iniciar Cámara Web",
            command=self._toggle_camera,
            fg_color=self.config.COLOR_ACCENT_SUCCESS,
            hover_color="#059669",
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38,
            corner_radius=10
        )
        self.btn_cam_toggle.pack(side="bottom", padx=12, pady=16, fill="x")


        # =====================================================================
        # COLUMNA 2: VISOR CENTRAL DE CÁMARA (EXPANDIDO & LIMPIO)
        # =====================================================================
        # =====================================================================
        # COLUMNA 2: VISOR CENTRAL DE CÁMARA (EXPANDIDO & LIMPIO)
        # =====================================================================
        self.center_viewport = ctk.CTkFrame(self, fg_color=self.config.COLOR_BG_DARK, corner_radius=0)
        self.center_viewport.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.center_viewport.grid_rowconfigure(1, weight=1)
        self.center_viewport.grid_columnconfigure(0, weight=1)
        self.center_viewport.grid_propagate(False)

        # Encabezado del visor (Estilo Breadcrumb minimalista)
        self.header_frame = ctk.CTkFrame(self.center_viewport, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        header_title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_title_box.pack(side="left")

        lbl_breadcrumb = ctk.CTkLabel(
            header_title_box,
            text="RUTINA ACTIVA",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        lbl_breadcrumb.pack(anchor="w")

        self.lbl_active_title = ctk.CTkLabel(
            header_title_box,
            text=self.active_strategy.name,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.config.COLOR_TEXT_MAIN
        )
        self.lbl_active_title.pack(anchor="w")

        self.btn_restart_routine = ctk.CTkButton(
            self.header_frame,
            text="🔄 Reiniciar Rutina",
            command=self._restart_current_routine,
            fg_color=self.config.COLOR_SURFACE,
            hover_color=self.config.COLOR_SURFACE_HOVER,
            text_color=self.config.COLOR_TEXT_SECONDARY,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            width=135,
            corner_radius=8
        )
        self.btn_restart_routine.pack(side="right")

        # Contenedor central (Video / Canvas de Respiración) con dimensiones fijas
        self.display_container = ctk.CTkFrame(
            self.center_viewport,
            fg_color=self.config.COLOR_BG_DARK,
            corner_radius=14,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE
        )
        self.display_container.grid(row=1, column=0, sticky="nsew", pady=2)
        self.display_container.grid_rowconfigure(0, weight=1)
        self.display_container.grid_columnconfigure(0, weight=1)
        self.display_container.grid_propagate(False)

        # Label para renderizar video de cámara limpio
        self.video_label = ctk.CTkLabel(
            self.display_container,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Widget de respiración (para modo triangular / 478)
        self.breathing_canvas = BreathingCanvasWidget(self.display_container, width=540, height=480, bg=self.config.COLOR_BG_DARK)

        # =====================================================================
        # COLUMNA 3: PANEL DERECHO (COACH VIRTUAL, GUÍA DETALLADA & BIOMETRÍA)
        # =====================================================================
        self.right_panel = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=self.config.COLOR_BG_SIDEBAR)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        self.right_panel.grid_propagate(False)

        # 1. Tarjeta Coach Virtual (Stickman Biomecánico) - Altura fija
        self.coach_card = ctk.CTkFrame(
            self.right_panel,
            fg_color=self.config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            height=250
        )
        self.coach_card.pack(fill="x", padx=14, pady=(16, 6))
        self.coach_card.pack_propagate(False)

        lbl_coach_header = ctk.CTkLabel(
            self.coach_card,
            text="GUÍA BIOMECÁNICA (COACH)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        lbl_coach_header.pack(pady=(8, 2))

        self.lbl_coach_display = ctk.CTkLabel(self.coach_card, text="", width=200, height=200)
        self.lbl_coach_display.pack(pady=(2, 8))

        # 2. Tarjeta de Estado de Postura en Vivo (Sentado vs De Pie) - Altura fija
        self.posture_card = ctk.CTkFrame(
            self.right_panel,
            fg_color=self.config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            height=76
        )
        self.posture_card.pack(fill="x", padx=14, pady=4)
        self.posture_card.pack_propagate(False)

        lbl_posture_hdr = ctk.CTkLabel(
            self.posture_card,
            text="POSTURA DETECTADA (IA)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        lbl_posture_hdr.pack(pady=(8, 1), padx=14, anchor="w")

        self.lbl_posture_badge = ctk.CTkLabel(
            self.posture_card,
            text="🪑 Sentado en escritorio",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.config.COLOR_ACCENT_ZEN
        )
        self.lbl_posture_badge.pack(pady=(0, 2), padx=14, anchor="w")

        self.lbl_posture_rec = ctk.CTkLabel(
            self.posture_card,
            text="Recomendado: 🪑 Sentado o 🧍 De pie",
            font=ctk.CTkFont(size=10),
            text_color=self.config.COLOR_TEXT_MUTED
        )
        self.lbl_posture_rec.pack(pady=(0, 8), padx=14, anchor="w")

        # 3. Tarjeta de Ejercicio e Instrucciones Detalladas - Altura fija
        self.guide_card = ctk.CTkFrame(
            self.right_panel,
            fg_color=self.config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            height=142
        )
        self.guide_card.pack(fill="x", padx=14, pady=4)
        self.guide_card.pack_propagate(False)

        self.lbl_exercise_step = ctk.CTkLabel(
            self.guide_card,
            text="PASO 1 DE 5",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.config.COLOR_ACCENT_PRIMARY
        )
        self.lbl_exercise_step.pack(pady=(8, 1), padx=14, anchor="w")

        self.lbl_exercise_title = ctk.CTkLabel(
            self.guide_card,
            text="Estiramiento de Muñecas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.config.COLOR_TEXT_MAIN
        )
        self.lbl_exercise_title.pack(pady=(0, 1), padx=14, anchor="w")

        self.lbl_exercise_target = ctk.CTkLabel(
            self.guide_card,
            text="Prevención del Síndrome del Túnel Carpiano",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color=self.config.COLOR_ACCENT_SUCCESS
        )
        self.lbl_exercise_target.pack(pady=(0, 4), padx=14, anchor="w")

        self.lbl_exercise_steps = ctk.CTkLabel(
            self.guide_card,
            text="1. Extiende el brazo al frente.\n2. Jala los dedos suavemente hacia atrás.\n3. Mantén 10 segundos.",
            font=ctk.CTkFont(size=11),
            text_color=self.config.COLOR_TEXT_SECONDARY,
            justify="left"
        )
        self.lbl_exercise_steps.pack(pady=(0, 8), padx=14, anchor="w")

        # 4. Tarjeta de Métrica, Temporizador y Progreso - Altura fija
        self.telemetry_card = ctk.CTkFrame(
            self.right_panel,
            fg_color=self.config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=self.config.COLOR_BORDER_SUBTLE,
            height=100
        )
        self.telemetry_card.pack(fill="x", padx=14, pady=4)
        self.telemetry_card.pack_propagate(False)


        self.lbl_digital_counter = ctk.CTkLabel(
            self.telemetry_card,
            text="00 / 10s",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.config.COLOR_ACCENT_SUCCESS
        )
        self.lbl_digital_counter.pack(pady=(8, 2))

        self.telemetry_progressbar = ctk.CTkProgressBar(
            self.telemetry_card,
            height=6,
            corner_radius=3,
            progress_color=self.config.COLOR_ACCENT_SUCCESS,
            fg_color=self.config.COLOR_BORDER_SUBTLE
        )
        self.telemetry_progressbar.pack(fill="x", padx=14, pady=4)
        self.telemetry_progressbar.set(0.0)

        self.lbl_feedback_msg = ctk.CTkLabel(
            self.telemetry_card,
            text="Ponte frente a la cámara para iniciar.",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.config.COLOR_TEXT_MAIN
        )
        self.lbl_feedback_msg.pack(pady=(2, 10), padx=10)


    def _subscribe_events(self):
        self.event_bus.subscribe(AppEvent.REP_COMPLETED, self._on_rep_event)
        self.event_bus.subscribe(AppEvent.BREATH_CYCLE_DONE, self._on_breath_cycle_event)

    def _on_rep_event(self, data):
        reps = data.get("reps", 0)
        if hasattr(self, 'lbl_digital_counter'):
            self.lbl_digital_counter.configure(text=f"Reps: {reps}")
        if hasattr(self, 'lbl_feedback_msg') and "evaluation" in data:
            self.lbl_feedback_msg.configure(text=str(data['evaluation']))

    def _on_breath_cycle_event(self, data):
        cycles = data.get("cycles", 0)
        if hasattr(self, 'lbl_digital_counter'):
            self.lbl_digital_counter.configure(text=f"Ciclos: {cycles} / 3")

    def _update_right_panel_static_info(self):
        """Actualiza la guía del ejercicio en el panel derecho según la rutina activa."""
        if self.active_strategy.category == "gamificacion":
            step_id = getattr(self.active_strategy, "exercises", [{}])[0].get("id", "ESTIRAMIENTO_MUNECA")
            detail = get_exercise_detail(step_id)
            self.lbl_exercise_step.configure(text=f"Paso 1 de {len(self.active_strategy.exercises)}")
            self.lbl_exercise_title.configure(text=detail["title"])
            self.lbl_exercise_target.configure(text=detail["target"])
            self.lbl_exercise_steps.configure(text="\n".join(detail["steps"]))
            self.lbl_posture_rec.configure(text=f"Recomendado: {detail['recommended_posture']}")
            self.lbl_digital_counter.configure(text="00 / 10s")
        elif self.active_strategy.category == "estiramiento":
            detail = get_exercise_detail("CUELLO_IZQ")
            self.lbl_exercise_step.configure(text="Paso 1 de 3")
            self.lbl_exercise_title.configure(text=detail["title"])
            self.lbl_exercise_target.configure(text=detail["target"])
            self.lbl_exercise_steps.configure(text="\n".join(detail["steps"]))
            self.lbl_posture_rec.configure(text=f"Recomendado: {detail['recommended_posture']}")
            self.lbl_digital_counter.configure(text="0.0s / 3.5s")
        elif self.active_strategy.category == "fisica":
            detail = get_exercise_detail("SENTADILLA")
            self.lbl_exercise_step.configure(text="Serie de 10 Repeticiones")
            self.lbl_exercise_title.configure(text=detail["title"])
            self.lbl_exercise_target.configure(text=detail["target"])
            self.lbl_exercise_steps.configure(text="\n".join(detail["steps"]))
            self.lbl_posture_rec.configure(text=f"Recomendado: {detail['recommended_posture']}")
            self.lbl_digital_counter.configure(text="0 / 10 REPS")
        elif self.active_strategy.category == "respiracion":
            mode_key = "RESPIRA_TRIANGULO" if getattr(self.active_strategy, "mode", "") == "triangular" else "RESPIRA_478"
            detail = get_exercise_detail(mode_key)
            self.lbl_exercise_step.configure(text="Ciclos de Relajación")
            self.lbl_exercise_title.configure(text=detail["title"])
            self.lbl_exercise_target.configure(text=detail["target"])
            self.lbl_exercise_steps.configure(text="\n".join(detail["steps"]))
            self.lbl_posture_rec.configure(text=f"Recomendado: {detail['recommended_posture']}")
            self.lbl_digital_counter.configure(text="Ciclo 1 de 3")

        # Actualizar avatar inicial correspondiente a la rutina seleccionada
        pose_key = "RESPIRA_ZEN" if self.active_strategy.category == "respiracion" else (
            "SENTADILLA" if self.active_strategy.category == "fisica" else (
                "CUELLO_IZQ" if self.active_strategy.category == "estiramiento" else "SALUDO"
            )
        )
        av_img = CoachAvatar.render_pose(pose_key, 0, size=(200, 200))
        av_rgb = cv2.cvtColor(av_img, cv2.COLOR_BGR2RGB)
        av_pil = Image.fromarray(av_rgb).resize((200, 200), Image.Resampling.LANCZOS)
        av_ctk = ctk.CTkImage(light_image=av_pil, dark_image=av_pil, size=(200, 200))
        self.lbl_coach_display.configure(image=av_ctk, text="")

    def _select_routine(self, routine_type: str):
        # Desmarcar botones al estilo sutil minimalista
        buttons = [self.btn_dance, self.btn_stretch, self.btn_squat, self.btn_breath_triangle, self.btn_breath_478]
        for b in buttons:
            b.configure(
                fg_color="transparent",
                border_width=0,
                text_color=self.config.COLOR_TEXT_SECONDARY,
                font=ctk.CTkFont(size=12)
            )

        active_btn = self.btn_dance
        if routine_type == "dance":
            self.active_strategy = self.dance_strategy
            active_btn = self.btn_dance
            self.breathing_canvas.grid_forget()
            self.video_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        elif routine_type == "stretch":
            self.active_strategy = self.stretch_strategy
            active_btn = self.btn_stretch
            self.breathing_canvas.grid_forget()
            self.video_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        elif routine_type == "squat":
            self.active_strategy = self.squat_strategy
            active_btn = self.btn_squat
            self.breathing_canvas.grid_forget()
            self.video_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        elif routine_type == "triangle":
            self.breathing_triangle_strategy.set_mode("triangular")
            self.active_strategy = self.breathing_triangle_strategy
            active_btn = self.btn_breath_triangle
            self.video_label.grid_forget()
            self.breathing_canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        elif routine_type == "478":
            self.breathing_478_strategy.set_mode("478")
            self.active_strategy = self.breathing_478_strategy
            active_btn = self.btn_breath_478
            self.video_label.grid_forget()
            self.breathing_canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Resaltado limpio del botón activo
        active_btn.configure(
            fg_color=self.config.COLOR_SURFACE_HOVER,
            hover_color="#1e293b",
            border_width=1,
            border_color=self.config.COLOR_BORDER_STRONG,
            text_color=self.config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=12, weight="bold")
        )

        self.lbl_active_title.configure(text=self.active_strategy.name)
        self.active_strategy.reset()
        self._update_right_panel_static_info()

        # Si es respiración y la cámara no está corriendo, arrancar el ciclo de animación del canvas
        if self.active_strategy.category == "respiracion" and not self.is_camera_running:
            self._tick_breathing()

    def _restart_current_routine(self):
        """Reinicia el estado del ejercicio activo para comenzar de nuevo."""
        if self.active_strategy:
            self.active_strategy.reset()
            self._update_right_panel_static_info()
            self.lbl_feedback_msg.configure(text="Rutina reiniciada. ¡Listo!")
            if self.active_strategy.category == "respiracion" and not self.is_camera_running:
                self._tick_breathing()

    def _render_breathing_pacer(self, metrics: dict):
        """Renderiza el pacer de respiración tanto en modo autónomo como cuando la cámara está activa."""
        mode = metrics.get("mode", "triangular")
        if mode == "triangular":
            self.breathing_canvas.draw_triangle_pacer(
                phase_name=metrics.get("phase_name", "INHALA"),
                phase_index=metrics.get("phase_index", 0),
                progress=metrics.get("phase_progress", 0.0),
                remaining_secs=metrics.get("remaining_seconds", 3.5),
                instruction=metrics.get("instruction", ""),
                cycles=metrics.get("cycles_completed", 0)
            )
        else:
            self.breathing_canvas.draw_circular_478_pacer(
                phase_name=metrics.get("phase_name", "INHALA"),
                progress=metrics.get("phase_progress", 0.0),
                remaining_secs=metrics.get("remaining_seconds", 4.0),
                instruction=metrics.get("instruction", ""),
                cycles=metrics.get("cycles_completed", 0)
            )

    def _tick_breathing(self):
        """Ciclo continuo a 30 FPS para animar la respiración geométrica cuando la cámara está apagada."""
        if self.active_strategy.category == "respiracion" and not self.is_camera_running:
            metrics = self.active_strategy.process_frame(None, (480, 640))
            self._render_breathing_pacer(metrics)

            cycles = metrics.get("cycles_completed", 0)
            tgt = metrics.get("target_cycles", 3)
            self.lbl_digital_counter.configure(text=f"Ciclo {cycles + 1} / {tgt}")
            self.telemetry_progressbar.set(metrics.get("phase_progress", 0.0))
            self.lbl_feedback_msg.configure(text=metrics.get("instruction", "Respira en calma"))

            # Continuar refrescando mientras permanezca en modo respiración
            self.after(33, self._tick_breathing)

    def _show_camera_standby(self):
        """Genera una vista de cámara en reposo nítida y minimalista."""
        standby = np.zeros((520, 740, 3), dtype=np.uint8)
        standby[:] = (22, 13, 9) # #090D16 en BGR
        cx, cy = 370, 260
        cv2.rectangle(standby, (cx - 190, cy - 65), (cx + 190, cy + 65), (38, 23, 17), -1)
        cv2.rectangle(standby, (cx - 190, cy - 65), (cx + 190, cy + 65), (56, 38, 28), 1)

        (tw1, _), _ = cv2.getTextSize("CAMARA EN ESPERA", cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        cv2.putText(standby, "CAMARA EN ESPERA", (cx - tw1 // 2, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (248, 250, 252), 2, cv2.LINE_AA)

        (tw2, _), _ = cv2.getTextSize("Pulsa 'Iniciar Camara Web' para reactivar el analisis", cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(standby, "Pulsa 'Iniciar Camara Web' para reactivar el analisis", (cx - tw2 // 2, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (148, 163, 184), 1, cv2.LINE_AA)

        rgb = cv2.cvtColor(standby, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(rgb)
        ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(740, 520))
        self.video_label.configure(image=ctk_img, text="")

    def _toggle_camera(self):
        if not self.is_camera_running:
            self._start_camera()
        else:
            self._stop_camera()

    def _start_camera(self):
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)

        if not self.cap.isOpened():
            self.video_label.configure(text="⚠️ No se detectó ninguna cámara web conectada.\nVerifica que la cámara esté disponible o usa el modo respiración.")
            return

        self.is_camera_running = True
        self.btn_cam_toggle.configure(text="⏹ Detener Cámara", fg_color=self.config.COLOR_ACCENT_DANGER, hover_color="#dc2626")
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()

    def _stop_camera(self):
        self.is_camera_running = False
        if hasattr(self, 'dance_strategy') and hasattr(self.dance_strategy, 'video_player'):
            self.dance_strategy.video_player.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_cam_toggle.configure(text="📷 Iniciar Cámara Web", fg_color=self.config.COLOR_ACCENT_SUCCESS, hover_color="#059669")
        
        # Limpiar completamente el visor y mostrar pantalla de espera
        self._show_camera_standby()

        # Si estamos en respiración, reanudar el ciclo de animación inmediatamente
        if self.active_strategy.category == "respiracion":
            self._tick_breathing()


    def _camera_loop(self):
        while self.is_camera_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    time.sleep(0.03)
                    continue

                frame = cv2.flip(frame, 1) # Efecto espejo natural
                h, w = frame.shape[:2]

                # Detección de poses con MediaPipe
                landmarks = None
                if self.detector_ready and self.pose_detector:
                    try:
                        landmarks = self.pose_detector.detect(frame)
                        if landmarks:
                            frame = self.pose_detector.draw_skeleton(frame, landmarks)
                    except Exception as e:
                        print(f"[Error PoseDetector]: {e}")

                # Procesamiento de la estrategia activa
                metrics = self.active_strategy.process_frame(landmarks, (h, w))

                # Actualizar GUI en el hilo principal
                self.after(0, self._update_gui_from_metrics, frame, metrics)
            except Exception:
                import traceback
                traceback.print_exc()

            time.sleep(1.0 / self.config.FPS_TARGET)

    def _update_gui_from_metrics(self, frame: np.ndarray, metrics: dict):
        h, w = frame.shape[:2]

        # =====================================================================
        # 1. ACTUALIZAR PANEL DERECHO (TELEMETRÍA & INSTRUCCIONES DETALLADAS)
        # =====================================================================
        # Coach Virtual Stickman
        if "avatar_img" in metrics and metrics["avatar_img"] is not None:
            av = metrics["avatar_img"]
            av_rgb = cv2.cvtColor(av, cv2.COLOR_BGR2RGB)
            av_pil = Image.fromarray(av_rgb).resize((200, 200), Image.Resampling.LANCZOS)
            av_ctk = ctk.CTkImage(light_image=av_pil, dark_image=av_pil, size=(200, 200))
            self.lbl_coach_display.configure(image=av_ctk, text="")

        # Detección de Postura en Tiempo Real (Sentado / De Pie)
        posture_label = metrics.get("user_posture", "Buscando postura...")
        posture_icon = metrics.get("user_posture_icon", "👤")
        self.lbl_posture_badge.configure(text=f"{posture_icon} {posture_label}")

        # Guía Detallada del Ejercicio Actual
        pose_id = metrics.get("pose_id", "ESTIRAMIENTO_MUNECA")
        detail = get_exercise_detail(pose_id)
        step_str = metrics.get("step_str", "Pausa Activa")
        self.lbl_exercise_step.configure(text=step_str)
        self.lbl_exercise_title.configure(text=detail["title"])
        self.lbl_exercise_target.configure(text=detail["target"])
        self.lbl_exercise_steps.configure(text="\n".join(detail["steps"]))
        self.lbl_posture_rec.configure(text=f"Recomendado: {detail['recommended_posture']}")

        # Contador Digital y Barra de Progreso según la rutina
        is_completed = metrics.get("is_completed", False)
        is_matched = metrics.get("is_matched", False)
        ex_type = metrics.get("type", "")

        if self.active_strategy.category == "gamificacion":
            if ex_type == "calf_raises":
                calf_r = metrics.get("calf_reps", 0)
                tgt = metrics.get("target_reps", 10)
                self.lbl_digital_counter.configure(text=f"{calf_r} / {tgt} REPS", text_color=self.config.COLOR_ACCENT_SUCCESS)
                self.telemetry_progressbar.set(min(1.0, calf_r / float(tgt)))
            else:
                elapsed = metrics.get("elapsed_sec", 0.0)
                total = metrics.get("total_sec", 6.0)
                color = self.config.COLOR_ACCENT_SUCCESS if is_matched else self.config.COLOR_ACCENT_ZEN
                self.lbl_digital_counter.configure(text=f"{int(elapsed):02d}s / {int(total):02d}s", text_color=color)
                self.telemetry_progressbar.set(metrics.get("progress_ratio", 0.0))

            self.lbl_feedback_msg.configure(text=metrics.get("feedback", "Sigue la postura del Coach"))

            # Sutil indicador sobre la mano si aplica
            hand_pt = metrics.get("hand_highlight")
            if hand_pt and not is_completed:
                cv2.circle(frame, hand_pt, 14, (16, 185, 129), 2)
                cv2.circle(frame, hand_pt, 8, (16, 185, 129), -1)

        elif self.active_strategy.category == "estiramiento":
            step = metrics.get("step", 0)
            step_titles = ["Paso 1/3: Cuello a la Izquierda", "Paso 2/3: Cuello a la Derecha", "Paso 3/3: Brazos al Cielo"]
            if step < len(step_titles):
                self.lbl_exercise_step.configure(text=step_titles[step])

            rem = metrics.get("hold_sec_remaining", 0.0)
            prog = metrics.get("hold_progress", 0.0)
            color = self.config.COLOR_ACCENT_SUCCESS if metrics.get("is_stretching") else self.config.COLOR_ACCENT_ZEN
            self.lbl_digital_counter.configure(text=f"{rem:.1f}s sostenidos", text_color=color)
            self.telemetry_progressbar.set(prog)
            self.lbl_feedback_msg.configure(text=metrics.get("feedback", ""))

            # Flecha guía direccional sutil en pantalla
            head_pt = metrics.get("head_pt")
            direction = metrics.get("direction", "LEFT")
            if head_pt and not is_completed:
                draw_direction_indicator(frame, direction, head_pt, tick=metrics.get("tick", 0), color=(56, 189, 248))

        elif self.active_strategy.category == "fisica":
            reps = metrics.get("reps", 0)
            tgt = metrics.get("target_reps", 10)
            self.lbl_digital_counter.configure(text=f"{reps} / {tgt} REPS", text_color=self.config.COLOR_ACCENT_SUCCESS)
            self.telemetry_progressbar.set(min(1.0, reps / float(tgt)))
            self.lbl_feedback_msg.configure(text=metrics.get("feedback", ""))

        elif self.active_strategy.category == "respiracion":
            cycles = metrics.get("cycles_completed", 0)
            tgt = metrics.get("target_cycles", 3)
            self.lbl_digital_counter.configure(text=f"Ciclo {cycles + 1} / {tgt}", text_color=self.config.COLOR_ACCENT_ZEN)
            self.telemetry_progressbar.set(metrics.get("phase_progress", 0.0))
            self.lbl_feedback_msg.configure(text=metrics.get("instruction", "Respira en calma"))
            self._render_breathing_pacer(metrics)


        # =====================================================================
        # 2. OVERLAY CENTRAL DE CELEBRACIÓN (SOLO CUANDO TERMINA LA RUTINA)
        # =====================================================================
        if is_completed:
            overlay = frame.copy()
            box_w, box_h = min(500, w - 40), 120
            bx1 = (w - box_w) // 2
            by1 = (h - box_h) // 2
            cv2.rectangle(overlay, (bx1, by1), (bx1 + box_w, by1 + box_h), (15, 23, 42), -1)
            cv2.addWeighted(overlay, 0.90, frame, 0.10, 0, frame)
            cv2.rectangle(frame, (bx1, by1), (bx1 + box_w, by1 + box_h), (34, 197, 94), 2)
            draw_pill_text(frame, "RUTINA COMPLETADA CON EXITO", (bx1 + 25, by1 + 42), font_scale=0.72, text_color=(34, 197, 94), thickness=2)
            draw_pill_text(frame, "Articulaciones protegidas. Pulsa 'Reiniciar Rutina'", (bx1 + 25, by1 + 84), font_scale=0.48, text_color=(250, 204, 21), thickness=1)

        # =====================================================================
        # 3. ESCALAR Y RENDERIZAR VIDEO LIMPIO Y AMPLIO EN TKINTER
        # =====================================================================
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img = img.resize((740, 520), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(740, 520))
        self.video_label.configure(image=ctk_img, text="")

    def _update_work_timer(self):
        """Temporizador de oficina que cuenta regresivamente para la pausa activa."""
        if not self.is_break_active:
            if self.time_until_break_seconds > 0:
                self.time_until_break_seconds -= 1
            else:
                self._trigger_break_alert()

        mins = self.time_until_break_seconds // 60
        secs = self.time_until_break_seconds % 60
        self.timer_display.configure(text=f"{mins:02d}:{secs:02d}")

        # Programar siguiente segundo
        self.after(1000, self._update_work_timer)

    def _manual_start_break(self):
        self.time_until_break_seconds = self.config.BREAK_DURATION_MINUTES * 60
        self.is_break_active = True
        self.timer_card.configure(border_width=2, border_color="#22c55e")
        self.btn_trigger_break.configure(text="Terminar Pausa", fg_color="#ef4444", hover_color="#dc2626", command=self._finish_break)
        if not self.is_camera_running:
            self._start_camera()

    def _trigger_break_alert(self):
        self.event_bus.publish(AppEvent.BREAK_ALERT)
        self._manual_start_break()

    def _finish_break(self):
        self.is_break_active = False
        summary = self.active_strategy.get_summary()

        # Guardar en base de datos SQLite
        self.history_db.record_session(
            category=self.active_strategy.category,
            routine_name=self.active_strategy.name,
            reps=summary.get("repeticiones_totales", 0),
            cycles=summary.get("ciclos_completados", 0),
            evaluation=summary.get("diagnostico_fisico", summary.get("beneficio_alcanzado", ""))
        )

        self.time_until_break_seconds = self.config.WORK_INTERVAL_MINUTES * 60
        self.timer_card.configure(border_width=1, border_color="#1e293b")
        self.btn_trigger_break.configure(text="Hacer Pausa Ahora", fg_color="#0284c7", hover_color="#0369a1", command=self._manual_start_break)
        self.lbl_feedback_msg.configure(text="¡Pausa completada con éxito! Progreso guardado.")

    def _open_exercise_editor(self):
        """Abre la ventana modal para personalizar y agregar nuevos ejercicios."""
        def on_saved():
            self.dance_strategy.reload_exercises()
            self._update_right_panel_static_info()
            self.lbl_feedback_msg.configure(text="¡Rutina de ejercicios actualizada con éxito!")

        editor = ExerciseEditorWindow(self, on_saved_callback=on_saved)
        editor.grab_set()

    def _on_close(self):
        """Cierre ordenado y limpio de la aplicación y liberación de recursos."""
        self.is_camera_running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        if hasattr(self, "dance_strategy") and hasattr(self.dance_strategy, "video_player"):
            try:
                self.dance_strategy.video_player.stop()
            except Exception:
                pass
        self.destroy()
