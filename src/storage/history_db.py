"""
Módulo de almacenamiento y base de datos local SQLite.
Registra el historial de sentadillas, sesiones de respiración anti-estrés
y calcula las métricas de acondicionamiento físico acumuladas.
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

class HistoryDB:
    def __init__(self, db_path: str = "pausas_activas.db"):
        self.db_path = db_path
        self._is_memory = (db_path == ":memory:")
        self._mem_conn = sqlite3.connect(":memory:") if self._is_memory else None
        self._init_db()

    def _get_connection(self):
        if self._is_memory:
            return self._mem_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                routine_name TEXT NOT NULL,
                reps INTEGER DEFAULT 0,
                cycles INTEGER DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0,
                evaluation TEXT
            )
        """)
        conn.commit()
        if not self._is_memory:
            conn.close()

    def record_session(self, category: str, routine_name: str, reps: int = 0,
                       cycles: int = 0, duration_seconds: int = 0, evaluation: str = ""):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (timestamp, category, routine_name, reps, cycles, duration_seconds, evaluation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, routine_name, reps, cycles, duration_seconds, evaluation))
        conn.commit()
        if not self._is_memory:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(reps), SUM(cycles), COUNT(*) FROM sessions")
        row = cursor.fetchone()
        total_reps = row[0] or 0
        total_cycles = row[1] or 0
        total_sessions = row[2] or 0

        # Sentadillas de hoy
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(reps) FROM sessions WHERE timestamp LIKE ?", (f"{today}%",))
        today_reps = cursor.fetchone()[0] or 0
        if not self._is_memory:
            conn.close()

        return {
            "total_sessions": total_sessions,
            "total_reps": total_reps,
            "today_reps": today_reps,
            "total_cycles": total_cycles,
            "calories_burned": round(total_reps * 0.32, 1),
            "physical_rating": self._calculate_overall_health_level(total_reps)
        }

    def _calculate_overall_health_level(self, total_reps: int) -> str:
        if total_reps < 20:
            return "Nivel Inicial: Activando movilidad contra el sedentarismo."
        elif total_reps < 60:
            return "Nivel Moderado: Excelente reducción de tensión lumbar y activación circulatoria."
        elif total_reps < 120:
            return "Nivel Consistente: Gran tonificación en tren inferior y salud cardiovascular."
        else:
            return "Nivel Atleta de Oficina: Óptima resistencia muscular y postura corporal de acero."
