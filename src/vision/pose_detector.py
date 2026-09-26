"""
Detector Holístico de Cuerpo y Manos con MediaPipe Tasks Vision.
Combina PoseLandmarker (Full Body 33 puntos) con HandLandmarker (Manos y Dedos 21 puntos cada una).
Ofrece máxima precisión para movimientos de manos, brazos y torso frente a la cámara web.
"""
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Optional, List, Tuple, Dict, Any

# Conexiones anatómicas principales para el cuerpo
POSE_CONNECTIONS = [
    (11, 12), # Hombro a hombro
    (11, 13), (13, 15), # Brazo izq
    (12, 14), (14, 16), # Brazo der
    (11, 23), (12, 24), # Torso
    (23, 24), # Cadera a cadera
    (23, 25), (25, 27), # Pierna izq
    (24, 26), (26, 28)  # Pierna der
]

# Conexiones de las 21 articulaciones de cada mano
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),        # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),   # Medio
    (9, 13), (13, 14), (14, 15), (15, 16), # Anular
    (13, 17), (17, 18), (18, 19), (19, 20),# Meñique
    (0, 17)                                 # Base palma
]

class HolisticData:
    """Contenedor compatible con listas que almacena tanto Pose como Manos detalladas."""
    def __init__(self, pose_landmarks, hand_landmarks_list=None):
        self.pose = pose_landmarks
        self.hands = hand_landmarks_list or []

    def __getitem__(self, idx):
        if self.pose is not None:
            return self.pose[idx]
        raise IndexError("No pose landmarks detected")

    def __len__(self):
        return len(self.pose) if self.pose is not None else 0

    def __bool__(self):
        return bool((self.pose is not None) or (len(self.hands) > 0))

    def get(self, key, default=None):
        if key == "pose":
            return self.pose
        elif key == "hands":
            return self.hands
        return default

class PoseDetector:
    """Detector multimodal de Pose y Manos de alta resolución."""

    def __init__(self,
                 pose_model_path: str = "models/pose_landmarker_full.task",
                 hand_model_path: str = "models/hand_landmarker.task"):
        def resolve_model_path(p: str) -> str:
            if os.path.exists(p):
                return p
            if getattr(sys, 'frozen', False):
                base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
                cand = os.path.join(base, p)
                if os.path.exists(cand):
                    return cand
            return p

        pose_model_path = resolve_model_path(pose_model_path)
        hand_model_path = resolve_model_path(hand_model_path)

        # Fallback a lite si full no estuviera disponible
        if not os.path.exists(pose_model_path):
            pose_model_path = resolve_model_path("models/pose_landmarker_lite.task")
        if not os.path.exists(pose_model_path):
            raise FileNotFoundError(f"No se encontró el modelo de pose en: {pose_model_path}")

        # 1. Detector de Pose (Cuerpo Completo)
        pose_base = python.BaseOptions(model_asset_path=pose_model_path)
        pose_options = vision.PoseLandmarkerOptions(
            base_options=pose_base,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.45,
            min_pose_presence_confidence=0.45,
            min_tracking_confidence=0.45
        )
        self.pose_detector = vision.PoseLandmarker.create_from_options(pose_options)

        # 2. Detector de Manos (21 puntos por mano, dedos y palmas)
        self.hand_detector = None
        if os.path.exists(hand_model_path):
            try:
                hand_base = python.BaseOptions(model_asset_path=hand_model_path)
                hand_options = vision.HandLandmarkerOptions(
                    base_options=hand_base,
                    running_mode=vision.RunningMode.IMAGE,
                    num_hands=2,
                    min_hand_detection_confidence=0.35,
                    min_hand_presence_confidence=0.35,
                    min_tracking_confidence=0.35
                )
                self.hand_detector = vision.HandLandmarker.create_from_options(hand_options)
            except Exception as e:
                print(f"[Aviso] No se pudo inicializar HandLandmarker: {e}")

    def detect(self, bgr_frame: np.ndarray) -> Optional[HolisticData]:
        """
        Detecta simultáneamente la pose corporal y las articulaciones de ambas manos.
        """
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detección corporal
        pose_lms = None
        try:
            pose_res = self.pose_detector.detect(mp_image)
            if pose_res.pose_landmarks and len(pose_res.pose_landmarks) > 0:
                pose_lms = pose_res.pose_landmarks[0]
        except Exception:
            pass

        # Detección de manos
        hands_lms = []
        if self.hand_detector:
            try:
                hand_res = self.hand_detector.detect(mp_image)
                if hand_res.hand_landmarks:
                    hands_lms = hand_res.hand_landmarks
            except Exception:
                pass

        if pose_lms is None and len(hands_lms) == 0:
            return None

        return HolisticData(pose_lms, hands_lms)

    def draw_skeleton(self, frame: np.ndarray, landmarks, accent_color=(34, 197, 94)) -> np.ndarray:
        """
        Dibuja el esqueleto del cuerpo y las articulaciones detalladas de los dedos de ambas manos.
        """
        if landmarks is None:
            return frame

        h, w, _ = frame.shape

        # Extraer pose y manos
        pose_pts = landmarks.pose if hasattr(landmarks, "pose") else landmarks
        hands_list = landmarks.hands if hasattr(landmarks, "hands") else []

        # 1. Dibujar articulaciones corporales
        if pose_pts is not None:
            points: Dict[int, Tuple[int, int]] = {}
            for idx, lm in enumerate(pose_pts):
                if hasattr(lm, "visibility") and lm.visibility is not None and lm.visibility < 0.35:
                    continue
                cx, cy = int(lm.x * w), int(lm.y * h)
                points[idx] = (cx, cy)
                cv2.circle(frame, (cx, cy), 4, accent_color, -1)
                cv2.circle(frame, (cx, cy), 6, (255, 255, 255), 1)

            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx in points and end_idx in points:
                    cv2.line(frame, points[start_idx], points[end_idx], (255, 255, 255), 2)
                    cv2.line(frame, points[start_idx], points[end_idx], accent_color, 1)

        # 2. Dibujar articulaciones de los dedos y palmas de cada mano
        for hand in hands_list:
            hand_pts: Dict[int, Tuple[int, int]] = {}
            for idx, lm in enumerate(hand):
                hx, hy = int(lm.x * w), int(lm.y * h)
                hand_pts[idx] = (hx, hy)
                # Yemas de los dedos en cian brillante
                pt_color = (6, 182, 212) if idx in [4, 8, 12, 16, 20] else (56, 189, 248)
                radius = 4 if idx in [4, 8, 12, 16, 20] else 3
                cv2.circle(frame, (hx, hy), radius, pt_color, -1)

            # Dibujar falanges y huesos de la mano
            for start_idx, end_idx in HAND_CONNECTIONS:
                if start_idx in hand_pts and end_idx in hand_pts:
                    cv2.line(frame, hand_pts[start_idx], hand_pts[end_idx], (6, 182, 212), 2)

        return frame

class PoseDetectorFactory:
    """Patrón Factory para instanciar el detector de poses según configuración."""
    @staticmethod
    def create_detector(model_path: str = "models/pose_landmarker_full.task") -> PoseDetector:
        return PoseDetector(pose_model_path=model_path, hand_model_path="models/hand_landmarker.task")
