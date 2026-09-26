"""
Pruebas de validación de pipeline biomecánico, patrones de diseño y estrategias.
"""
import sys
import os
import unittest
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.geometry import calculate_angle_2d, calculate_slope_angle
from src.patterns.observer import EventBus, AppEvent
from src.patterns.state import StateManager, AppState
from src.strategies.squat_strategy import SquatStrategy
from src.strategies.breathing_strategy import BreathingStrategy
from src.strategies.stretch_strategy import StretchStrategy
from src.storage.history_db import HistoryDB

class TestPausasActivasPipeline(unittest.TestCase):
    def test_geometry_angle_90_degrees(self):
        # Ángulo recto en (0, 0)
        p1 = (0.0, 100.0) # Arriba (Cadera)
        p2 = (0.0, 0.0)   # Vértice (Rodilla)
        p3 = (100.0, 0.0) # Derecha (Tobillo)
        angle = calculate_angle_2d(p1, p2, p3)
        self.assertAlmostEqual(angle, 90.0, places=1)

    def test_geometry_angle_180_degrees(self):
        # Línea recta (de pie)
        p1 = (0.0, 100.0)
        p2 = (0.0, 50.0)
        p3 = (0.0, 0.0)
        angle = calculate_angle_2d(p1, p2, p3)
        self.assertAlmostEqual(angle, 180.0, places=1)

    def test_squat_strategy_counter_and_evaluation(self):
        strat = SquatStrategy()
        self.assertEqual(strat.reps_count, 0)
        
        # Simular landmarks para posición DOWN (90 grados)
        class DummyLandmark:
            def __init__(self, x, y, vis=0.9):
                self.x, self.y, self.visibility = x, y, vis

        landmarks = [DummyLandmark(0.5, 0.5) for _ in range(33)]
        # Cadera (23), Rodilla (25), Tobillo (27) formando 90°
        landmarks[23] = DummyLandmark(0.5, 0.2)
        landmarks[25] = DummyLandmark(0.5, 0.5)
        landmarks[27] = DummyLandmark(0.8, 0.5)

        res_down = strat.process_frame(landmarks, (480, 640))
        self.assertEqual(strat.stage, "DOWN")

        # Ahora subir a 180°
        landmarks[27] = DummyLandmark(0.5, 0.8)
        res_up = strat.process_frame(landmarks, (480, 640))
        self.assertEqual(strat.stage, "UP")
        self.assertEqual(strat.reps_count, 1)
        self.assertIn("1 reps", strat.get_fitness_evaluation())

    def test_breathing_strategy_phases(self):
        strat = BreathingStrategy(mode="triangular")
        res = strat.process_frame(None, (480, 640))
        self.assertEqual(res["mode"], "triangular")
        self.assertEqual(res["total_phases"], 3)
        self.assertIn(res["phase_name"], ["INHALA", "MANTÉN", "EXHALA"])

    def test_observer_event_bus(self):
        bus = EventBus()
        received = []
        def listener(data):
            received.append(data)
        bus.subscribe(AppEvent.REP_COMPLETED, listener)
        bus.publish(AppEvent.REP_COMPLETED, {"test": 123})
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["test"], 123)

    def test_dance_game_strategy(self):
        from src.strategies.dance_game_strategy import DanceGameStrategy
        strat = DanceGameStrategy()
        # Estado inicial touchless
        res_greet = strat.process_frame(None, (480, 640))
        self.assertEqual(res_greet["pose_id"], "SALUDO_INICIO")
        self.assertIn("avatar_img", res_greet)
        self.assertEqual(res_greet["avatar_img"].shape, (190, 190, 3))

        # Tras saludar, avanza a muñecas
        strat.waiting_for_greeting = False
        res = strat.process_frame(None, (480, 640))
        self.assertEqual(res["pose_id"], "ESTIRAMIENTO_MUNECA")
        self.assertIn("avatar_img", res)
        self.assertEqual(res["avatar_img"].shape, (190, 190, 3))
        self.assertIn("progress_pct", res)

if __name__ == "__main__":
    unittest.main()
