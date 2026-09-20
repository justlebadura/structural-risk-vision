"""Sección 2 - ArUco: corrección de perspectiva y escala real.

Detecta el marcador ArUco en la imagen, calcula la matriz de homografía
(vista cenital) y la escala cm/píxel usando el tamaño real conocido del
marcador. No depende de modelos entrenados: es puramente OpenCV.
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
        """Detecta el marcador y devuelve esquinas, homografía y escala.

        sensor_stability es opcional y se propaga desde la captura (Sección 1).
        """
        if not self.available or image is None:
            return {"detected": False, "message": "OpenCV/ArUco no disponible."}

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._detector.detectMarkers(gray)

        if ids is None or len(ids) == 0:
            return {"detected": False, "message": "No se detectó marcador ArUco."}

        # Tomamos el primer marcador
        marker_corners = corners[0][0]  # 4x2
        marker_id = int(ids[0][0])

        # Estimación del ángulo de captura con el detector de pose del marcador
        orientation = "cenital_ok"
        if aruco is not None and hasattr(aruco, "estimatePoseSingleMarkers"):
            try:
                rvecs, _, _ = aruco.estimatePoseSingleMarkers(
                    corners, config.REAL_MARKER_SIZE_CM, None, None
                )
                rvec = rvecs[0][0]
                # Ángulo de elevación (inclinación de la cámara respecto a la normal)
                elevation_deg = np.degrees(np.linalg.norm(rvec))
                if elevation_deg > 45:
                    orientation = "angulo_incorrecto"
                else:
                    orientation = "cenital_ok"
            except Exception:
                pass

        # Escala real: cm/píxel a partir del lado real conocido y su proyección
        side_px = np.mean(
            [np.linalg.norm(marker_corners[i] - marker_corners[(i + 1) % 4])
             for i in range(4)]
        )
        scale_cm_per_px = config.REAL_MARKER_SIZE_CM / side_px if side_px > 0 else None
        if scale_cm_per_px is not None:
            scale_cm_per_px = float(scale_cm_per_px)

        # Homografía hacia una vista cenital (cuadrado de tamaño normalizado)
        dst_size = config.NORM_SIZE
        dst = np.array(
            [[0, 0], [dst_size - 1, 0], [dst_size - 1, dst_size - 1], [0, dst_size - 1]],
            dtype=np.float32,
        )
        H, _ = cv2.findHomography(marker_corners.astype(np.float32), dst)
        homography = H.tolist() if H is not None else None

        stability = sensor_stability or "estable"
        return {
            "detected": True,
            "marker_id": marker_id,
            "corners": marker_corners.astype(float).tolist(),
            "homography": homography,
            "scale_cm_per_px": scale_cm_per_px,
            "orientation": orientation,
            "stability": stability,
            "message": "Marcador detectado y escala calibrada.",
        }

    def warp_cenital(self, image: np.ndarray, homography: list) -> Optional[np.ndarray]:
        """Aplica la homografía para obtener la vista cenital de la imagen."""
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