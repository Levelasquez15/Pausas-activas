"""
Patrón Observer (Publicador - Suscriptor)
Permite desacoplar el procesamiento de la cámara/IA de la interfaz gráfica y los sonidos.
"""
from typing import Callable, Dict, List, Any
from enum import Enum, auto

class AppEvent(Enum):
    REP_COMPLETED = auto()       # Se completó una repetición válida (ej. sentadilla)
    POSTURE_WARNING = auto()     # Postura incorrecta o encorvamiento
    POSTURE_CORRECT = auto()     # Postura óptima restablecida
    BREATH_PHASE_CHANGE = auto() # Cambio de fase respiratoria (Inhala -> Mantén -> Exhala)
    BREATH_CYCLE_DONE = auto()   # Ciclo de respiración completado
    BREAK_ALERT = auto()         # Es momento de la pausa activa
    BREAK_FINISHED = auto()      # Fin de la pausa activa

class EventBus:
    """Bus central de eventos mediante el patrón Observer."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers: Dict[AppEvent, List[Callable[[Any], None]]] = {
                event: [] for event in AppEvent
            }
        return cls._instance

    def subscribe(self, event: AppEvent, callback: Callable[[Any], None]) -> None:
        """Suscribe una función callback a un evento específico."""
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: AppEvent, callback: Callable[[Any], None]) -> None:
        """Desuscribe una función callback."""
        if callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)

    def publish(self, event: AppEvent, data: Any = None) -> None:
        """Notifica a todos los suscriptores registrados para el evento."""
        for callback in self._subscribers[event]:
            try:
                callback(data)
            except Exception as e:
                print(f"[EventBus] Error en callback para {event.name}: {e}")
