import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.strategies.dance_game_strategy import DanceGameStrategy
from src.ui.video_guide_player import VideoGuidePlayer
from src.ui.coach_avatar import CoachAvatar

class TestErgonomicCatalog(unittest.TestCase):
    def setUp(self):
        self.strategy = DanceGameStrategy()

    def test_exercise_catalog_loaded(self):
        exercises = self.strategy.exercises
        self.assertEqual(len(exercises), 8)
        ids = [ex["id"] for ex in exercises]
        self.assertIn("ESTIRAMIENTO_MUNECA", ids)
        self.assertIn("HOMBROS_CIRCULOS", ids)
        self.assertIn("APERTURA_PECHO", ids)
        self.assertIn("INCLINACION_CUELLO", ids)
        self.assertIn("ESTIRAMIENTO_TRICEPS", ids)
        self.assertIn("TORSION_TRONCO", ids)
        self.assertIn("BRAZOS_ARRIBA", ids)
        self.assertIn("BOMBEO_PANTORRILLAS", ids)

    def test_video_player_singleton(self):
        p1 = VideoGuidePlayer()
        p2 = VideoGuidePlayer()
        self.assertIs(p1, p2)
        frame = p1.get_frame("ESTIRAMIENTO_MUNECA", size=(190, 190))
        # Como el video de muñecas ya existe en assets/videos/, retorna el frame procesado
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (190, 190, 3))
        # Para un ejercicio sin video, debe retornar None
        frame_none = p1.get_frame("EJERCICIO_INEXISTENTE_XYZ", size=(190, 190))
        self.assertIsNone(frame_none)

    def test_coach_avatar_ergonomic_poses(self):
        poses = [
            "ESTIRAMIENTO_MUNECA",
            "HOMBROS_CIRCULOS",
            "APERTURA_PECHO",
            "INCLINACION_CUELLO",
            "ESTIRAMIENTO_TRICEPS",
            "TORSION_TRONCO",
            "EXTENSION_LUMBAR",
            "BRAZOS_ARRIBA",
            "BOMBEO_PANTORRILLAS",
            "COMPLETED",
            "SENTADILLA",
            "RESPIRA",
            "SALUDO",
            "GESTO_PULGAR"
        ]
        for pose in poses:
            img = CoachAvatar.render_pose(pose, tick=10, size=(190, 190))
            self.assertEqual(img.shape, (190, 190, 3))

    def test_process_frame_wrist_stretch(self):
        # 1. Primer estado: Saludo inicial touchless
        res_greet = self.strategy.process_frame(None, (480, 640))
        self.assertEqual(res_greet["pose_id"], "SALUDO_INICIO")

        # 2. Desactivar espera de saludo para avanzar al primer ejercicio ergonómico
        self.strategy.waiting_for_greeting = False
        res = self.strategy.process_frame(None, (480, 640))
        self.assertEqual(res["pose_id"], "ESTIRAMIENTO_MUNECA")
        self.assertEqual(res["type"], "wrist_stretch")
        self.assertIn("avatar_img", res)
        self.assertIn("progress_pct", res)
        self.assertFalse(res["is_matched"])
        self.assertFalse(res["is_completed"])

    def test_dance_game_completion_stops(self):
        self.strategy.waiting_for_greeting = False
        # Simular llegar al último ejercicio y completarlo
        self.strategy.current_step_index = len(self.strategy.exercises) - 1
        self.strategy.calf_reps = 10
        # Forzar completado
        self.strategy.is_completed = True
        res_completed = self.strategy.process_frame(None, (480, 640))
        self.assertTrue(res_completed["is_completed"])
        self.assertEqual(res_completed["pose_id"], "FINALIZACION_GESTO")

    def test_resting_posture_does_not_match(self):
        class MockPoint:
            def __init__(self, x, y, z=0.0, visibility=0.9):
                self.x, self.y, self.z, self.visibility = x, y, z, visibility

        # Crear esqueleto simulado de usuario sentado normalmente con brazos doblados
        pts = [MockPoint(0.5, 0.2)] * 33 # 0 = nose
        pts[11] = MockPoint(0.38, 0.40) # sh_l
        pts[12] = MockPoint(0.62, 0.40) # sh_r
        pts[13] = MockPoint(0.32, 0.62) # el_l (codos abajo doblados)
        pts[14] = MockPoint(0.68, 0.62) # el_r
        pts[15] = MockPoint(0.46, 0.74) # w_l (muñecas en el regazo)
        pts[16] = MockPoint(0.54, 0.74) # w_r

        self.strategy.waiting_for_greeting = False
        res = self.strategy.process_frame(pts, (480, 640))
        # No debe dar positivo falso
        self.assertFalse(res["is_matched"])
        self.assertIn("Extiende", res["feedback"])

    def test_wrist_stretch_front_facing_matches(self):
        class MockPoint:
            def __init__(self, x, y, z=0.0, visibility=0.9):
                self.x, self.y, self.z, self.visibility = x, y, z, visibility

        # Usuario de frente estirando dedos con la otra mano a la altura del pecho
        pts = [MockPoint(0.5, 0.2)] * 33 # 0 = nose
        pts[11] = MockPoint(0.38, 0.40, z=0.0) # sh_l
        pts[12] = MockPoint(0.62, 0.40, z=0.0) # sh_r
        pts[13] = MockPoint(0.42, 0.50, z=-0.08) # el_l
        pts[14] = MockPoint(0.58, 0.50, z=-0.08) # el_r
        pts[15] = MockPoint(0.48, 0.52, z=-0.18) # w_l (frente al pecho hacia la cámara)
        pts[16] = MockPoint(0.52, 0.52, z=-0.15) # w_r (asistiendo)

        self.strategy.waiting_for_greeting = False
        res = self.strategy.process_frame(pts, (480, 640))
        # Debe reconocer de frente
        self.assertTrue(res["is_matched"])
        self.assertIn("túnel carpiano", res["feedback"])

if __name__ == "__main__":
    unittest.main()
