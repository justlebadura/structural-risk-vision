"""Sección 1 - Captura (Marcador ArUco + guía por giróscopo).

La cámara vive en el dispositivo del cliente (celular/webcam). Este módulo
gestiona la *sesión* de captura y evalúa la estabilidad usando los datos de
sensor que el frontend envía junto a cada frame. El procesamiento pesado se
delega a aruco/preprocess.
"""
from __future__ import annotations

import math
import time
import uuid
from typing import Optional

import numpy as np

from core import config


def classify_surface(sensor: Optional[dict]) -> dict:
    """Determina la superficie (techo / piso / pared) desde el acelerómetro.

    Usa la dirección de la gravedad en el marco del dispositivo. Convención
    (Expo/Android): con la pantalla hacia arriba `az > 0`; la cámara trasera
    apunta hacia abajo → **piso**. Pantalla hacia abajo → **techo**. Dispositivo
    vertical (gravedad en el plano de la pantalla) → **pared**.

    Devuelve `{surface, tilt_deg, source}`. `tilt_deg` es el ángulo del plano del
    dispositivo respecto a la horizontal.
    """
    accel = (sensor or {}).get("accel")
    if not accel or len(accel) != 3:
        return {"surface": "indeterminado", "tilt_deg": None, "source": "sin_sensor"}

    ax, ay, az = (float(v) for v in accel)
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if norm == 0:
        return {"surface": "indeterminado", "tilt_deg": None, "source": "sin_sensor"}

    nz = az / norm
    tilt_deg = math.degrees(math.acos(min(abs(nz), 1.0)))

    if abs(nz) >= config.SURFACE_HORIZONTAL_AZ:
        surface = "piso" if nz >= 0 else "techo"
    elif abs(nz) <= config.SURFACE_VERTICAL_AZ:
        surface = "pared"
    else:
        surface = "indeterminado"

    return {"surface": surface, "tilt_deg": round(tilt_deg, 1), "source": "acelerometro"}


class CameraSession:
    """Sesión lógica de captura. No abre hardware; recibe frames del cliente."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.active = True
        self.frame_count = 0
        self.last_capture_at: Optional[str] = None
        self.latest_frame: Optional[np.ndarray] = None

    def feed(self, image: Optional[np.ndarray], sensor: Optional[dict]) -> dict:
        """Registra un frame y devuelve el estado de estabilidad y superficie.

        Usa la magnitud de rotación del giróscopo como guía de estabilidad:
        si es baja, la captura es "estable". El acelerómetro indica la superficie.
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

        return {"stability": stability, "message": message, **classify_surface(sensor)}

    def stop(self) -> None:
        self.active = False


def start_session() -> CameraSession:
    return CameraSession()


def capture_best_frame(session: CameraSession) -> Optional[np.ndarray]:
    """Devuelve el frame más reciente almacenado en la sesión."""
    return session.latest_frame