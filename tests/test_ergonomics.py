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

    def test_triceps_stretch_bilateral_progression(self):
        class MockPoint:
            def __init__(self, x, y, z=0.0, visibility=0.9):
                self.x, self.y, self.z, self.visibility = x, y, z, visibility

        import time

        # Posicionarse en ESTIRAMIENTO_TRICEPS (índice 4 en catálogo de 8)
        self.strategy.waiting_for_greeting = False
        triceps_idx = [i for i, ex in enumerate(self.strategy.exercises) if ex["id"] == "ESTIRAMIENTO_TRICEPS"][0]
        self.strategy.current_step_index = triceps_idx

        # 1. Fase 1: Brazo izquierdo del usuario (codo en pantalla izquierda x < 0.5)
        # MediaPipe landmarks:
        # sh_r en x=0.38, sh_l en x=0.62 (shoulder_line_y = 0.40)
        # codo izq en pantalla: el_r (x=0.32, y=0.25 -> por encima de hombros)
        # codo der en pantalla: el_l (x=0.65, y=0.55 -> abajo)
        pts_left_arm = [MockPoint(0.5, 0.2)] * 33
        pts_left_arm[11] = MockPoint(0.62, 0.40) # sh_l
        pts_left_arm[12] = MockPoint(0.38, 0.40) # sh_r
        pts_left_arm[13] = MockPoint(0.65, 0.55) # el_l (abajo)
        pts_left_arm[14] = MockPoint(0.32, 0.25) # el_r (arriba en pantalla izquierda = brazo izquierdo)

        res1 = self.strategy.process_frame(pts_left_arm, (480, 640))
        self.assertTrue(res1["is_matched"])
        self.assertEqual(self.strategy.current_side_phase, 1)

        # Simular 4.1 segundos para completar Fase 1
        self.strategy.hold_start_time = time.time() - 4.1
        res1_done = self.strategy.process_frame(pts_left_arm, (480, 640))
        self.assertEqual(self.strategy.current_side_phase, 2)
        self.assertEqual(self.strategy.side_1_detected, "LEFT")
        # En Fase 2, la guía DEBE apuntar a la DERECHA
        self.assertEqual(res1_done["guide_direction"], "RIGHT")

        # Si el usuario insiste con el brazo izquierdo en Fase 2, no debe hacer match y avisa cambiar a Derecho
        res_repeat_left = self.strategy.process_frame(pts_left_arm, (480, 640))
        self.assertFalse(res_repeat_left["is_matched"])
        self.assertIn("Derecho", res_repeat_left["warning_msg"])

        # 2. Fase 2: Ahora eleva el brazo derecho (codo en pantalla derecha x > 0.5)
        pts_right_arm = [MockPoint(0.5, 0.2)] * 33
        pts_right_arm[11] = MockPoint(0.62, 0.40) # sh_l
        pts_right_arm[12] = MockPoint(0.38, 0.40) # sh_r
        pts_right_arm[13] = MockPoint(0.65, 0.25) # el_l (arriba en pantalla derecha = brazo derecho)
        pts_right_arm[14] = MockPoint(0.32, 0.55) # el_r (abajo)

        res2 = self.strategy.process_frame(pts_right_arm, (480, 640))
        self.assertTrue(res2["is_matched"])

        # Simular 4.1 segundos para completar Fase 2
        self.strategy.hold_start_time = time.time() - 4.1
        res2_done = self.strategy.process_frame(pts_right_arm, (480, 640))
        # Debe haber avanzado al siguiente ejercicio
        self.assertEqual(self.strategy.current_step_index, triceps_idx + 1)
        self.assertEqual(self.strategy.current_side_phase, 1)

    def test_trunk_twist_bilateral_progression(self):
        class MockPoint:
            def __init__(self, x, y, z=0.0, visibility=0.9):
                self.x, self.y, self.z, self.visibility = x, y, z, visibility

        import time

        self.strategy.waiting_for_greeting = False
        twist_idx = [i for i, ex in enumerate(self.strategy.exercises) if ex["id"] == "TORSION_TRONCO"][0]
        self.strategy.current_step_index = twist_idx

        # 1. Giro a la izquierda: nariz desplazada hacia la izquierda (x=0.42 con hombros en 0.38 y 0.62, centro 0.50)
        # orejas: oreja izq (ear_r) en x=0.40, oreja der (ear_l) en x=0.58
        pts_twist_left = [MockPoint(0.42, 0.2)] * 33 # nose en 0.42
        pts_twist_left[11] = MockPoint(0.62, 0.40) # sh_l
        pts_twist_left[12] = MockPoint(0.38, 0.40) # sh_r
        pts_twist_left[7] = MockPoint(0.58, 0.20)  # ear_l
        pts_twist_left[8] = MockPoint(0.40, 0.20)  # ear_r

        res1 = self.strategy.process_frame(pts_twist_left, (480, 640))
        self.assertTrue(res1["is_matched"])
        self.assertEqual(self.strategy.current_side_phase, 1)

        # Simular 4.1s para terminar Lado 1
        self.strategy.hold_start_time = time.time() - 4.1
        res1_done = self.strategy.process_frame(pts_twist_left, (480, 640))
        self.assertEqual(self.strategy.current_side_phase, 2)
        self.assertEqual(self.strategy.side_1_detected, "LEFT")
        # En Fase 2, la guía DEBE exigir rotar a la DERECHA
        self.assertEqual(res1_done["guide_direction"], "RIGHT")

        # Si insiste a la izquierda, no empareja y pide Derecha
        res_repeat_left = self.strategy.process_frame(pts_twist_left, (480, 640))
        self.assertFalse(res_repeat_left["is_matched"])
        self.assertIn("Derech", res_repeat_left["warning_msg"])

        # 2. Giro a la derecha: nariz desplazada hacia la derecha (x=0.58)
        pts_twist_right = [MockPoint(0.58, 0.2)] * 33 # nose en 0.58
        pts_twist_right[11] = MockPoint(0.62, 0.40) # sh_l
        pts_twist_right[12] = MockPoint(0.38, 0.40) # sh_r
        pts_twist_right[7] = MockPoint(0.60, 0.20)  # ear_l
        pts_twist_right[8] = MockPoint(0.42, 0.20)  # ear_r

        res2 = self.strategy.process_frame(pts_twist_right, (480, 640))
        self.assertTrue(res2["is_matched"])

        # Simular 4.1s para terminar Lado 2
        self.strategy.hold_start_time = time.time() - 4.1
        res2_done = self.strategy.process_frame(pts_twist_right, (480, 640))
        self.assertEqual(self.strategy.current_step_index, twist_idx + 1)
        self.assertEqual(self.strategy.current_side_phase, 1)

if __name__ == "__main__":
    unittest.main()
