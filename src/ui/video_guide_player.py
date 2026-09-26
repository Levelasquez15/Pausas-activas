"""
Reproductor de Video y Audio Guía para Ejercicios de Pausas Activas.
Permite al usuario colocar archivos de video (.mp4, .avi, .mov, .mkv) en `assets/videos/`.
El sistema sincroniza la reproducción del video en bucle y emite el audio correspondiente
usando la API multimedia nativa de Windows (MCI winmm.dll).
Si no hay video para un ejercicio, retorna None para permitir el fallback al Coach Avatar.
"""
import os
import glob
import ctypes
import cv2
import numpy as np
from typing import Optional, Dict

class VideoGuidePlayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoGuidePlayer, cls).__new__(cls)
            cls._instance._init_player()
        return cls._instance

    def _init_player(self):
        self.videos_dir = os.path.abspath("assets/videos")
        self.current_key: Optional[str] = None
        self.current_cap: Optional[cv2.VideoCapture] = None
        self.current_video_path: Optional[str] = None
        self.audio_playing: bool = False
        self._mci = ctypes.windll.winmm.mciSendStringW if hasattr(ctypes, 'windll') else None
        
        # Reproductor COM nativo de Windows (reproduce audio de cualquier archivo .mp4/.avi/.mov con audio integrado)
        self._wmp = None
        try:
            import win32com.client
            self._wmp = win32com.client.Dispatch("WMPlayer.OCX")
            self._wmp.settings.setMode("loop", True)
            self._wmp.settings.volume = 95
        except Exception:
            self._wmp = None

        self.exercise_keywords: Dict[str, list] = {
            "muneca": ["1", "muneca", "wrist", "carpiano"],
            "pecho": ["2", "pecho", "escapul", "chest", "retraccion"],
            "cuello": ["3", "cuello", "neck", "cervical", "inclinacion"],
            "torsion": ["4", "torsion", "tronco", "twist", "lumbar"],
            "pantorrillas": ["5", "pantorrilla", "calf", "puntillas", "talon"]
        }

    def _normalize(self, text: str) -> str:
        import unicodedata
        nfd = unicodedata.normalize('NFD', text.lower())
        without_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        return without_accents.replace('ñ', 'n').replace('_', ' ').replace('-', ' ')

    def _find_video_for_exercise(self, exercise_id: str) -> Optional[str]:
        if not os.path.exists(self.videos_dir):
            return None

        clean_id = self._normalize(exercise_id)
        keywords = []
        for cat, kw_list in self.exercise_keywords.items():
            if any(k in clean_id for k in kw_list):
                keywords = kw_list
                break
        if not keywords:
            keywords = [clean_id[:5]]

        valid_exts = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        all_files = os.listdir(self.videos_dir)

        for fname in all_files:
            base, ext = os.path.splitext(fname)
            if ext.lower() in valid_exts:
                fname_norm = self._normalize(base)
                for kw in keywords:
                    if kw.isdigit():
                        if fname_norm.startswith(kw) or f" {kw} " in f" {fname_norm} ":
                            return os.path.join(self.videos_dir, fname)
                    elif kw in fname_norm:
                        return os.path.join(self.videos_dir, fname)

        return None

    def _stop_audio(self):
        if self._wmp:
            try:
                self._wmp.controls.stop()
            except Exception:
                pass
        if self._mci:
            try:
                self._mci('stop vid_audio', None, 0, None)
                self._mci('close vid_audio', None, 0, None)
            except Exception:
                pass
        self.audio_playing = False

    def _start_audio(self, video_path: str):
        self._stop_audio()
        if not os.path.exists(video_path):
            return

        # 1. Intentar con Windows Media Player (ideal para .mp4 con audio embebido)
        if self._wmp:
            try:
                self._wmp.URL = video_path
                self._wmp.controls.play()
                self.audio_playing = True
                return
            except Exception:
                pass

        # 2. Fallback con MCI DirectShow
        if self._mci:
            try:
                cmd_open = f'open "{video_path}" type mpegvideo alias vid_audio'
                res = self._mci(cmd_open, None, 0, None)
                if res == 0:
                    self._mci('play vid_audio repeat', None, 0, None)
                    self.audio_playing = True
            except Exception:
                self.audio_playing = False

    def get_frame(self, exercise_id: str, size: tuple = (190, 190)) -> Optional[np.ndarray]:
        """
        Obtiene el siguiente fotograma del video guía para el ejercicio especificado.
        Si no hay video disponible, retorna None.
        """
        video_path = self._find_video_for_exercise(exercise_id)
        if not video_path:
            if self.current_cap:
                self.current_cap.release()
                self.current_cap = None
                self._stop_audio()
                self.current_key = None
            return None

        # Si cambió el video a reproducir
        if self.current_key != exercise_id or self.current_video_path != video_path:
            if self.current_cap:
                self.current_cap.release()
            self.current_cap = cv2.VideoCapture(video_path)
            self.current_key = exercise_id
            self.current_video_path = video_path
            self._start_audio(video_path)

        if not self.current_cap or not self.current_cap.isOpened():
            return None

        ret, frame = self.current_cap.read()
        if not ret or frame is None:
            # Reiniciar al inicio para bucle infinito
            self.current_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.current_cap.read()
            if not ret or frame is None:
                return None

        # Redimensionar al tamaño del widget/avatar
        w, h = size
        frame_resized = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)

        # Distintivo visual '▶ GUÍA DE VIDEO'
        cv2.rectangle(frame_resized, (0, h - 24), (w, h), (15, 23, 42), -1)
        cv2.putText(frame_resized, "▶ VIDEO GUIA", (10, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (34, 197, 94), 1, cv2.LINE_AA)

        return frame_resized

    def stop(self):
        """Detiene video y audio."""
        if self.current_cap:
            self.current_cap.release()
            self.current_cap = None
        self._stop_audio()
        self.current_key = None
        self.current_video_path = None
