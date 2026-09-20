"""Sección 1 - Captura (Marcador ArUco + guía por giróscopo).

La cámara vive en el dispositivo del cliente (celular/webcam). Este módulo
gestiona la *sesión* de captura y evalúa la estabilidad usando los datos de
sensor que el frontend envía junto a cada frame. El procesamiento pesado se
delega a aruco/preprocess.
"""
from __future__ import annotations

import time
import uuid
from typing import Optional

import numpy as np

from core import config


class CameraSession:
    """Sesión lógica de captura. No abre hardware; recibe frames del cliente."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.active = True
        self.frame_count = 0
        self.last_capture_at: Optional[str] = None
        self.latest_frame: Optional[np.ndarray] = None

    def feed(self, image: Optional[np.ndarray], sensor: Optional[dict]) -> dict:
        """Registra un frame y devuelve el estado de estabilidad.

        Usa la magnitud de rotación del giróscopo como guía de estabilidad:
        si es baja, la captura es "estable".
        """
        if image is not None:
            self.latest_frame = image
            self.frame_count += 1
            self.last_capture_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        stability = "estable"
        message = "Sin datos de sensor disponibles."
        if sensor and sensor.get("rotation"):
            rot = np.asarray(sensor["rotation"], dtype=float)
            magnitude = float(np.linalg.norm(rot))
            if magnitude > config.MAX_STABILITY_DEVIATION:
                stability = "inestable"
                message = f"Giro del sensor excede límite ({magnitude:.2f} rad/s)."
            else:
                message = f"Captura estable ({magnitude:.3f} rad/s)."

        return {"stability": stability, "message": message}

    def stop(self) -> None:
        self.active = False


def start_session() -> CameraSession:
    return CameraSession()


def capture_best_frame(session: CameraSession) -> Optional[np.ndarray]:
    """Devuelve el frame más reciente almacenado en la sesión."""
    return session.latest_frame