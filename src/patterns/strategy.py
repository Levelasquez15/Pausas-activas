"""
Patrón Strategy (Estrategia)
Define la interfaz abstracta que deben implementar tanto las rutinas físicas
(Sentadillas, Estiramiento) como las rutinas de relajación/respiración.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ExerciseStrategy(ABC):
    """Interfaz base para cualquier estrategia de pausa activa o ejercicio."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre legible de la rutina."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Categoría: 'fisica', 'respiracion', 'estiramiento'."""
        pass

    @abstractmethod
    def process_frame(self, landmarks, frame_shape: tuple) -> Dict[str, Any]:
        """
        Procesa los landmarks detectados por MediaPipe en el frame actual.
        Retorna un diccionario con métricas, repeticiones, estado y alertas.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reinicia el contador y el estado de la estrategia."""
        pass

    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        """Retorna el resumen final de la sesión realizada."""
        pass
