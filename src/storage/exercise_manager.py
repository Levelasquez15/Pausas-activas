"""
Gestor de Ejercicios y Rutinas Personalizables.
Permite al usuario listar, crear, editar y eliminar ejercicios para sus pausas activas
y sincronizarlos con TuxDance y las rutinas físicas.
"""
import json
import os
from typing import List, Dict, Any

DEFAULT_EXERCISES = [
    {
        "id": "ESTIRAMIENTO_MUNECA",
        "title": "Estiramiento de Muñecas",
        "subtitle": "Prevención del Túnel Carpiano",
        "desc": "Extiende el brazo al frente y empuja suavemente los dedos hacia atrás",
        "type": "wrist_stretch",
        "hold_sec": 10.0,
        "category": "ergonomico"
    },
    {
        "id": "HOMBROS_CIRCULOS",
        "title": "Rotación de Hombros",
        "subtitle": "Descarga de Trapecios y Escápulas",
        "desc": "Eleva los hombros hacia las orejas y rótalos suavemente hacia atrás en círculos",
        "type": "shoulder_roll",
        "hold_sec": 8.0,
        "category": "ergonomico"
    },
    {
        "id": "APERTURA_PECHO",
        "title": "Apertura de Pecho",
        "subtitle": "Retracción Escapular Anti-Joroba",
        "desc": "Echa hombros y codos atrás en 'W', junta escápulas y abre el pecho",
        "type": "chest_open",
        "hold_sec": 8.0,
        "category": "ergonomico"
    },
    {
        "id": "INCLINACION_CUELLO",
        "title": "Inclinación Lateral Cuello",
        "subtitle": "Liberación Cervical sin subir hombros",
        "desc": "Inclina lentamente la cabeza hacia el hombro manteniendo hombros relajados",
        "type": "neck_tilt",
        "hold_sec": 6.0,
        "category": "ergonomico"
    },
    {
        "id": "ESTIRAMIENTO_TRICEPS",
        "title": "Estiramiento de Tríceps",
        "subtitle": "Descompresión de Brazos y Dorsales",
        "desc": "Eleva un codo tras la cabeza y con la otra mano empújalo suavemente hacia atrás",
        "type": "triceps_stretch",
        "hold_sec": 8.0,
        "category": "ergonomico"
    },
    {
        "id": "TORSION_TRONCO",
        "title": "Torsión de Tronco",
        "subtitle": "Descarga Lumbar y Columna",
        "desc": "Con cadera fija al frente, gira suavemente los hombros y tronco a los lados",
        "type": "trunk_twist",
        "hold_sec": 8.0,
        "category": "ergonomico"
    },
    {
        "id": "EXTENSION_LUMBAR",
        "title": "Extensión Lumbar",
        "subtitle": "Descompresión Espinal y Espalda Baja",
        "desc": "Apoya manos en la cintura y arquea suavemente el torso hacia atrás abriendo el tórax",
        "type": "lumbar_extension",
        "hold_sec": 7.0,
        "category": "ergonomico"
    },
    {
        "id": "BRAZOS_ARRIBA",
        "title": "Brazos al Cielo",
        "subtitle": "Elongación Axial de Columna",
        "desc": "Eleva ambos brazos bien alto hacia el techo estirando toda la espalda",
        "type": "arms_up",
        "hold_sec": 7.0,
        "category": "ergonomico"
    },
    {
        "id": "BOMBEO_PANTORRILLAS",
        "title": "Bombeo de Pantorrillas",
        "subtitle": "Activación Circulatoria en Puntillas",
        "desc": "Elévate sobre las puntas de los pies y desciende rítmicamente (10 reps)",
        "type": "calf_raises",
        "target_reps": 10,
        "hold_sec": 0.5,
        "category": "ergonomico"
    }
]

class ExerciseManager:
    def __init__(self, filepath: str = "data/custom_exercises.json"):
        if not os.path.exists(filepath) and getattr(sys, 'frozen', False):
            base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            cand = os.path.join(base, filepath)
            if os.path.exists(cand):
                filepath = cand
        self.filepath = filepath
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self.exercises = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            self._save(DEFAULT_EXERCISES)
            return list(DEFAULT_EXERCISES)
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return list(DEFAULT_EXERCISES)

    def _save(self, exercises: List[Dict[str, Any]]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(exercises, f, indent=4, ensure_ascii=False)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.exercises)

    def add_exercise(self, title: str, desc: str, ex_type: str, hold_sec: float = 1.0, category: str = "personalizado"):
        new_id = f"EX_{len(self.exercises) + 1}_{title.upper().replace(' ', '_')}"
        item = {
            "id": new_id,
            "title": title.upper().replace(" ", "_"),
            "desc": desc,
            "type": ex_type,
            "hold_sec": float(hold_sec),
            "category": category
        }
        self.exercises.append(item)
        self._save(self.exercises)
        return item

    def update_exercise(self, index: int, title: str, desc: str, ex_type: str, hold_sec: float):
        if 0 <= index < len(self.exercises):
            self.exercises[index]["title"] = title.upper().replace(" ", "_")
            self.exercises[index]["desc"] = desc
            self.exercises[index]["type"] = ex_type
            self.exercises[index]["hold_sec"] = float(hold_sec)
            self._save(self.exercises)

    def delete_exercise(self, index: int):
        if 0 <= index < len(self.exercises) and len(self.exercises) > 1:
            self.exercises.pop(index)
            self._save(self.exercises)

    def reset_to_defaults(self):
        self.exercises = list(DEFAULT_EXERCISES)
        self._save(self.exercises)
