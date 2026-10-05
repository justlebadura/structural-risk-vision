"""Sección 2 - ArUco: corrección de perspectiva (vista cenital) y escala real.

Detecta el marcador ArUco, estima el **ángulo de inclinación** entre el plano
del marcador y el plano de la imagen (a partir de la geometría del cuadrilátero,
sin necesidad de calibración intrínseca), calcula la homografía hacia una vista
**cenital** (fronto-paralela) y la escala cm/píxel usando el tamaño real conocido
del marcador. No depende de modelos entrenados: es puramente OpenCV.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from core import config

try:
    import cv2
    from cv2 import aruco
except ImportError:  # pragma: no cover
    cv2 = None
    aruco = None


def _side_lengths(corners: np.ndarray) -> list[float]:
    """Longitudes de los 4 lados del cuadrilátero (arriba, der, abajo, izq)."""
    return [float(np.linalg.norm(corners[i] - corners[(i + 1) % 4])) for i in range(4)]


def estimate_tilt_deg(corners: np.ndarray) -> float:
    """Ángulo de inclinación (grados) entre el plano del marcador y la imagen.

    Sin calibración: un cuadrado visto en escorzo acorta un par de lados por
    `cos(θ)`. Con la razón entre lados opuestos se recupera el ángulo.
    """
    sides = _side_lengths(corners)
    top_bottom = (sides[0] + sides[2]) / 2.0
    left_right = (sides[1] + sides[3]) / 2.0
    longer, shorter = max(top_bottom, left_right), min(top_bottom, left_right)
    if longer <= 0:
        return 0.0
    ratio = float(np.clip(shorter / longer, 0.0, 1.0))
    return float(np.degrees(np.arccos(ratio)))


def estimate_roll_deg(corners: np.ndarray) -> float:
    """Rotación del marcador dentro del plano de la imagen (grados)."""
    dx = float(corners[1][0] - corners[0][0])
    dy = float(corners[1][1] - corners[0][1])
    return float(np.degrees(np.arctan2(dy, dx)))


class ArucoProcessor:
    def __init__(self) -> None:
        self._dict = None
        if aruco is not None:
            try:
                self._dict = aruco.getPredefinedDictionary(config.MARKER_DICT_ID)
                self._params = aruco.DetectorParameters()
                self._detector = aruco.ArucoDetector(self._dict, self._params)
            except Exception:
                self._dict = None

    @property
    def available(self) -> bool:
        return cv2 is not None and self._dict is not None

    def detect(self, image: np.ndarray, sensor_stability: Optional[str] = None) -> dict:
        """Detecta el marcador y devuelve esquinas, ángulo, homografía y escala."""
        if not self.available or image is None:
            return {"detected": False, "message": "OpenCV/ArUco no disponible."}

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._detector.detectMarkers(gray)

        if ids is None or len(ids) == 0:
            return {"detected": False, "message": "No se detectó marcador ArUco."}

        marker_corners = corners[0][0].astype(np.float32)  # 4x2
        marker_id = int(ids[0][0])

        # Ángulo de inclinación (perspectiva) y rotación en el plano de la imagen.
        tilt_deg = estimate_tilt_deg(marker_corners)
        roll_deg = estimate_roll_deg(marker_corners)
        cenital_ok = tilt_deg <= config.MAX_TILT_DEG
        orientation = "cenital_ok" if cenital_ok else "angulo_incorrecto"

        # Escala real: usamos el lado más largo (el menos acortado por el escorzo).
        side_px = max(_side_lengths(marker_corners))
        scale_cm_per_px = float(config.REAL_MARKER_SIZE_CM / side_px) if side_px > 0 else None

        # Homografía marcador → cuadrado fronto-paralelo (vista cenital).
        dst_size = config.NORM_SIZE
        dst = np.array(
            [[0, 0], [dst_size - 1, 0], [dst_size - 1, dst_size - 1], [0, dst_size - 1]],
            dtype=np.float32,
        )
        H, _ = cv2.findHomography(marker_corners, dst)
        homography = H.tolist() if H is not None else None

        stability = sensor_stability or "estable"
        return {
            "detected": True,
            "marker_id": marker_id,
            "corners": marker_corners.astype(float).tolist(),
            "homography": homography,
            "scale_cm_per_px": scale_cm_per_px,
            "tilt_deg": round(tilt_deg, 2),
            "roll_deg": round(roll_deg, 2),
            "cenital_ok": bool(cenital_ok),
            "orientation": orientation,
            "stability": stability,
            "message": (
                "Marcador detectado; vista cenital lista."
                if cenital_ok
                else f"Inclinación {tilt_deg:.1f}° > {config.MAX_TILT_DEG:.0f}°; "
                "reenfoca más perpendicular a la superficie."
            ),
        }

    def warp_cenital(self, image: np.ndarray, homography: list) -> Optional[np.ndarray]:
        """Aplica la homografía para obtener la vista cenital (fronto-paralela)."""
        if not self.available or image is None or homography is None:
            return None
        H = np.asarray(homography, dtype=np.float32)
        return cv2.warpPerspective(
            image, H, (config.NORM_SIZE, config.NORM_SIZE)
        )


_aruco_processor: Optional[ArucoProcessor] = None


def get_aruco_processor() -> ArucoProcessor:
    global _aruco_processor
    if _aruco_processor is None:
        _aruco_processor = ArucoProcessor()
    return _aruco_processor