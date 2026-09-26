"""
Patrón State (Máquina de Estados)
Controla el ciclo de vida del usuario en la jornada laboral y las pausas activas.
"""
from enum import Enum, auto

class AppState(Enum):
    WORKING = auto()           # Monitoreando tiempo de oficina en segundo plano
    BREAK_ALERT = auto()       # Alarma visual/sonora de pausa activa requerida
    EXERCISING_SQUAT = auto()  # Rutina activa de sentadillas con IA
    EXERCISING_STRETCH = auto()# Rutina de estiramientos de oficina
    BREATHING_TRIANGLE = auto()# Rutina de respiración triangular anti-estrés
    BREATHING_478 = auto()     # Rutina de respiración técnica 4-7-8
    SUMMARY = auto()           # Resumen de resultados, calorías y condición física

class StateManager:
    """Gestiona el estado global de la aplicación."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._current_state = AppState.WORKING
        return cls._instance

    @property
    def current_state(self) -> AppState:
        return self._current_state

    def set_state(self, new_state: AppState) -> None:
        print(f"[StateManager] Transición de estado: {self._current_state.name} -> {new_state.name}")
        self._current_state = new_state
