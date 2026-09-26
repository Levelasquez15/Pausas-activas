"""
Widget interactivo de Respiración Consciente (Canvas dinámico en Tkinter/CustomTkinter).
Renderiza el triángulo de TikTok y el pacer circular con una esfera que recorre la figura
en tiempo real para sincronizar la respiración.
"""
import tkinter as tk
import math
from typing import Dict, Any

class BreathingCanvasWidget(tk.Canvas):
    def __init__(self, master, width=380, height=340, bg="#090D16", **kwargs):
        super().__init__(master, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2 + 10

    def draw_triangle_pacer(self, phase_name: str, phase_index: int, progress: float,
                            remaining_secs: float, instruction: str, cycles: int):
        self.delete("all")

        if phase_name == "¡COMPLETADO!":
            self.create_oval(self.cx - 50, self.cy - 70, self.cx + 50, self.cy + 30, fill="#111726", outline="#38bdf8", width=2)
            self.create_text(self.cx, self.cy - 20, text="✨ 🧘 ✨", font=("Segoe UI", 26))
            self.create_text(self.cx, self.cy + 45, text="¡SESIÓN COMPLETADA!", fill="#38bdf8", font=("Segoe UI", 15, "bold"))
            self.create_text(self.cx, self.cy + 70, text=f"Completaste {cycles} ciclos de Respiración Triangular.", fill="#94a3b8", font=("Segoe UI", 11))
            self.create_text(self.cx, self.h - 18, text="Presiona 'Reiniciar Rutina' o selecciona otra actividad.", fill="#64748b", font=("Segoe UI", 10))
            return

        # Coordenadas del triángulo equilátero
        side = 200
        h_tri = side * (math.sqrt(3) / 2)
        v_top = (self.cx, self.cy - h_tri * 0.55)
        v_right = (self.cx + side / 2, self.cy + h_tri * 0.45)
        v_left = (self.cx - side / 2, self.cy + h_tri * 0.45)

        # Fondo sutil del triángulo con estética Refero
        self.create_polygon([v_top, v_right, v_left],
                            fill="#111726", outline="#1C2638", width=2, smooth=False)


        # Lado activo con resplandor
        active_color = "#38bdf8" # Celeste calma
        if phase_index == 0:
            # V_left -> V_top
            start_p, end_p = v_left, v_top
            active_line = [v_left, v_top]
        elif phase_index == 1:
            # V_top -> V_right
            start_p, end_p = v_top, v_right
            active_line = [v_top, v_right]
        else:
            # V_right -> V_left
            start_p, end_p = v_right, v_left
            active_line = [v_right, v_left]

        # Dibujar línea del lado activo en color brillante
        self.create_line(active_line[0][0], active_line[0][1], active_line[1][0], active_line[1][1],
                         fill=active_color, width=6, capstyle=tk.ROUND)

        # Posición de la esfera guía según el progreso (0.0 a 1.0)
        bx = start_p[0] + (end_p[0] - start_p[0]) * progress
        by = start_p[1] + (end_p[1] - start_p[1]) * progress

        # Esfera brillante con halo
        self.create_oval(bx - 14, by - 14, bx + 14, by + 14, fill="#0284c7", outline="")
        self.create_oval(bx - 9, by - 9, bx + 9, by + 9, fill="#38bdf8", outline="#ffffff", width=2)

        # Texto interior del triángulo
        self.create_text(self.cx, self.cy - 18, text=phase_name, fill="#ffffff",
                         font=("Helvetica", 20, "bold"))
        self.create_text(self.cx, self.cy + 15, text=f"{remaining_secs:.1f}s", fill="#38bdf8",
                         font=("Helvetica", 16, "bold"))
        self.create_text(self.cx, self.cy + 42, text=f"Ciclo #{cycles + 1}", fill="#94a3b8",
                         font=("Helvetica", 11))

        # Indicador inferior de instrucción
        self.create_text(self.cx, self.h - 20, text=instruction, fill="#cbd5e1",
                         font=("Helvetica", 11, "italic"))

    def draw_circular_478_pacer(self, phase_name: str, progress: float,
                                remaining_secs: float, instruction: str, cycles: int):
        self.delete("all")

        if phase_name == "¡COMPLETADO!":
            self.create_oval(self.cx - 50, self.cy - 70, self.cx + 50, self.cy + 30, fill="#111726", outline="#10B981", width=2)
            self.create_text(self.cx, self.cy - 20, text="✨ 🌬️ ✨", font=("Segoe UI", 26))
            self.create_text(self.cx, self.cy + 45, text="¡SESIÓN 4-7-8 COMPLETADA!", fill="#10B981", font=("Segoe UI", 15, "bold"))
            self.create_text(self.cx, self.cy + 70, text=f"Completaste {cycles} ciclos de Calma y Oxigenación.", fill="#94a3b8", font=("Segoe UI", 11))
            self.create_text(self.cx, self.h - 18, text="Presiona 'Reiniciar Rutina' o selecciona otra actividad.", fill="#64748b", font=("Segoe UI", 10))
            return

        radius = 95
        x0, y0 = self.cx - radius, self.cy - radius - 10
        x1, y1 = self.cx + radius, self.cy + radius - 10

        # Anillo base
        self.create_oval(x0, y0, x1, y1, outline="#1C2638", width=6)

        # Arco de progreso
        angle_extent = -360 * progress
        self.create_arc(x0, y0, x1, y1, start=90, extent=angle_extent,
                        outline="#10B981", width=6, style=tk.ARC)


        # Esfera orbital
        angle_rad = math.radians(90 + angle_extent)
        bx = self.cx + radius * math.cos(angle_rad)
        by = (self.cy - 10) - radius * math.sin(angle_rad)

        self.create_oval(bx - 12, by - 12, bx + 12, by + 12, fill="#16a34a", outline="")
        self.create_oval(bx - 8, by - 8, bx + 8, by + 8, fill="#4ade80", outline="#ffffff", width=2)

        # Textos centrales
        self.create_text(self.cx, self.cy - 25, text=phase_name, fill="#ffffff",
                         font=("Helvetica", 18, "bold"))
        self.create_text(self.cx, self.cy + 10, text=f"{remaining_secs:.1f}s", fill="#4ade80",
                         font=("Helvetica", 16, "bold"))
        self.create_text(self.cx, self.cy + 38, text=f"Ciclos: {cycles}", fill="#94a3b8",
                         font=("Helvetica", 11))

        # Subtexto de calma
        self.create_text(self.cx, self.h - 20, text=instruction, fill="#cbd5e1",
                         font=("Helvetica", 11, "italic"))
