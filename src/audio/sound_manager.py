"""
Módulo de Sonido y Notificaciones Auditivas.
Utiliza winsound nativo de Windows en hilos desacoplados (daemon) para
emitir chimes de retroalimentación en sentadillas y campanas relajantes en respiraciones.
"""
import threading
import sys
from src.patterns.observer import EventBus, AppEvent

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.enabled = True
            cls._instance._setup_event_listeners()
        return cls._instance

    def _setup_event_listeners(self):
        bus = EventBus()
        bus.subscribe(AppEvent.REP_COMPLETED, self._on_rep_completed)
        bus.subscribe(AppEvent.BREATH_PHASE_CHANGE, self._on_breath_phase)
        bus.subscribe(AppEvent.BREAK_ALERT, self._on_break_alert)

    def _play_tone(self, frequency: int, duration_ms: int):
        if not self.enabled:
            return
        if sys.platform == "win32":
            def run():
                try:
                    import winsound
                    winsound.Beep(frequency, duration_ms)
                except Exception:
                    pass
            threading.Thread(target=run, daemon=True).start()

    def _on_rep_completed(self, data):
        # Chime armónico ascendente al lograr sentadilla
        def chime():
            if sys.platform == "win32":
                try:
                    import winsound
                    winsound.Beep(784, 120) # Sol
                    winsound.Beep(1046, 200) # Do alto
                except Exception:
                    pass
        threading.Thread(target=chime, daemon=True).start()

    def _on_breath_phase(self, data):
        # Tono suave de transición zen (528 Hz - frecuencia de calma)
        self._play_tone(528, 250)

    def _on_break_alert(self, data):
        # Alarma de aviso de pausa activa
        def alert():
            if sys.platform == "win32":
                try:
                    import winsound
                    for _ in range(2):
                        winsound.Beep(880, 200)
                        winsound.Beep(659, 250)
                except Exception:
                    pass
        threading.Thread(target=alert, daemon=True).start()
