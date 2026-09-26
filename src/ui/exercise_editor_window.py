"""
Ventana / Diálogo para Agregar y Editar Ejercicios de Pausa Activa.
Diseño minimalista y limpio alineado al sistema de diseño Refero / Dark Obsidian.
"""
import customtkinter as ctk
from src.storage.exercise_manager import ExerciseManager

EXERCISE_TYPES = {
    "Estiramiento de Muñeca (Túnel Carpiano)": "wrist_stretch",
    "Apertura de Pecho (Anti-Joroba)": "chest_open",
    "Inclinación Lateral de Cuello": "neck_tilt",
    "Torsión de Tronco (Descarga Lumbar)": "trunk_twist",
    "Bombeo de Pantorrillas (Circulación)": "calf_raises",
    "Sentadilla Activa": "squat",
    "Postura Zen / Respiración": "zen_breath"
}

TYPE_TO_LABEL = {v: k for k, v in EXERCISE_TYPES.items()}

class ExerciseEditorWindow(ctk.CTkToplevel):
    def __init__(self, master, on_saved_callback=None):
        super().__init__(master)
        self.title("Personalizar Catálogo de Ejercicios")
        self.geometry("680x560")
        self.minsize(580, 500)
        self.configure(fg_color="#090D16")
        self.on_saved_callback = on_saved_callback
        self.manager = ExerciseManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Encabezado estilo Refero
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(18, 8), padx=24, sticky="ew")

        lbl_eyebrow = ctk.CTkLabel(
            header_frame,
            text="CONFIGURACIÓN / ERGONOMÍA",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#64748B"
        )
        lbl_eyebrow.pack(anchor="w")

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Catálogo de Ejercicios de Pausa Activa",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_title.pack(anchor="w")

        # Scrollable Frame para la lista de ejercicios
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#080B12",
            corner_radius=12,
            border_width=1,
            border_color="#1C2638"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Formulario para Agregar Nuevo Ejercicio
        form_frame = ctk.CTkFrame(
            self,
            fg_color="#111726",
            corner_radius=12,
            border_width=1,
            border_color="#1C2638"
        )
        form_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(8, 20))
        form_frame.grid_columnconfigure(1, weight=1)

        form_title = ctk.CTkLabel(
            form_frame,
            text="➕ Agregar Nuevo Ejercicio a la Rutina",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F8FAFC"
        )
        form_title.grid(row=0, column=0, columnspan=2, pady=(12, 8), padx=14, sticky="w")

        # Campo Título
        ctk.CTkLabel(
            form_frame,
            text="Nombre:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8"
        ).grid(row=1, column=0, padx=14, pady=4, sticky="w")

        self.ent_title = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ej: Estiramiento de Hombros",
            fg_color="#182236",
            border_color="#2B3952",
            text_color="#F8FAFC",
            placeholder_text_color="#64748B",
            corner_radius=8,
            height=32
        )
        self.ent_title.grid(row=1, column=1, padx=14, pady=4, sticky="ew")

        # Campo Descripción
        ctk.CTkLabel(
            form_frame,
            text="Instrucción:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8"
        ).grid(row=2, column=0, padx=14, pady=4, sticky="w")

        self.ent_desc = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ej: Lleva el brazo cruzado al pecho y sostén 10s",
            fg_color="#182236",
            border_color="#2B3952",
            text_color="#F8FAFC",
            placeholder_text_color="#64748B",
            corner_radius=8,
            height=32
        )
        self.ent_desc.grid(row=2, column=1, padx=14, pady=4, sticky="ew")

        # Selector de Tipo
        ctk.CTkLabel(
            form_frame,
            text="Patrón Biomecánico:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8"
        ).grid(row=3, column=0, padx=14, pady=4, sticky="w")

        self.combo_type = ctk.CTkComboBox(
            form_frame,
            values=list(EXERCISE_TYPES.keys()),
            fg_color="#182236",
            border_color="#2B3952",
            button_color="#2B3952",
            button_hover_color="#334155",
            dropdown_fg_color="#111726",
            text_color="#F8FAFC",
            corner_radius=8,
            height=32
        )
        self.combo_type.grid(row=3, column=1, padx=14, pady=4, sticky="ew")

        # Botón Guardar Nuevo
        btn_add = ctk.CTkButton(
            form_frame,
            text="Guardar en la Rutina",
            command=self._on_add,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            height=34
        )
        btn_add.grid(row=4, column=0, columnspan=2, pady=(12, 14), padx=14, sticky="ew")

        self._render_list()

    def _render_list(self):
        # Limpiar
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        exercises = self.manager.get_all()
        for idx, ex in enumerate(exercises):
            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="#111726",
                corner_radius=10,
                border_width=1,
                border_color="#1C2638"
            )
            card.pack(fill="x", pady=4, padx=6)
            card.grid_columnconfigure(0, weight=1)

            type_label = TYPE_TO_LABEL.get(ex.get("type", ""), ex.get("type", ""))
            lbl_title = ctk.CTkLabel(
                card,
                text=f"{idx + 1}. {ex['title']}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#F8FAFC"
            )
            lbl_title.grid(row=0, column=0, padx=14, pady=(8, 1), sticky="w")

            lbl_sub = ctk.CTkLabel(
                card,
                text=f"Patrón: {type_label}",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color="#38BDF8"
            )
            lbl_sub.grid(row=1, column=0, padx=14, pady=(0, 2), sticky="w")

            lbl_desc = ctk.CTkLabel(
                card,
                text=ex.get("desc", ""),
                font=ctk.CTkFont(size=11),
                text_color="#94A3B8"
            )
            lbl_desc.grid(row=2, column=0, padx=14, pady=(0, 8), sticky="w")

            # Botón Eliminar si hay más de 1
            if len(exercises) > 1:
                btn_del = ctk.CTkButton(
                    card,
                    text="Eliminar",
                    width=75,
                    height=28,
                    fg_color="transparent",
                    hover_color="#1F1518",
                    border_width=1,
                    border_color="#EF4444",
                    text_color="#EF4444",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    corner_radius=6,
                    command=lambda i=idx: self._on_delete(i)
                )
                btn_del.grid(row=0, column=1, rowspan=3, padx=14, pady=8)

    def _on_add(self):
        title = self.ent_title.get().strip()
        desc = self.ent_desc.get().strip()
        type_key = EXERCISE_TYPES.get(self.combo_type.get(), "wrist_stretch")

        if not title:
            title = "NUEVO_EJERCICIO"
        if not desc:
            desc = "¡Sigue la postura indicada frente a la cámara!"

        self.manager.add_exercise(title=title, desc=desc, ex_type=type_key, hold_sec=6.0)
        self.ent_title.delete(0, "end")
        self.ent_desc.delete(0, "end")
        self._render_list()

        if self.on_saved_callback:
            self.on_saved_callback()

    def _on_delete(self, idx: int):
        self.manager.delete_exercise(idx)
        self._render_list()
        if self.on_saved_callback:
            self.on_saved_callback()
