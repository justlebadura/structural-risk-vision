"""Modo demo — respuestas sintéticas para validar el frontend.

Solo se usa cuando `APP_MODE=demo` (ver core/config.py). Devuelve un reporte
de ejemplo con la MISMA forma que el pipeline real (core/schemas.py) para que
la interfaz se pueda probar de punta a punta sin marcador ArUco ni modelo
TFLite entrenado. No sustituye al pipeline real en producción.
"""
from __future__ import annotations

import numpy as np

from core import config

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

from services.images import encode_base64_image

# Escala "típica" demo (cm por píxel) y tamaño del área analizada.
DEMO_SCALE_CM_PER_PX = 0.033
DEMO_WIDTH_CM = 21.1
DEMO_HEIGHT_CM = 21.1
DEMO_TOTAL_PATCHES = 64
DEMO_CRACK_PATCHES = 27


def _demo_cenital_image() -> str:
    """Genera una imagen cenital sintética (concreto + grieta) en base64 JPEG."""
    h = w = 640
    if cv2 is None:
        img = np.full((h, w, 3), 128, dtype=np.uint8)
    else:
        rng = np.random.default_rng(0)
        img = np.clip(rng.normal(140, 14, (h, w, 3)), 0, 255).astype(np.uint8)
        pts = np.array(
            [[80, 120], [260, 300], [420, 340], [560, 380]], np.int32
        ).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], False, (30, 30, 30), 6)
        cv2.GaussianBlur(img, (3, 3), 0, img)
    return encode_base64_image(img)


def demo_analyze() -> dict:
    """Reporte de ejemplo con la estructura de AnalyzeResponse."""
    aruco = {
        "detected": True,
        "marker_id": config.MARKER_DICT_ID,
        "corners": [[220.0, 220.0], [420.0, 220.0], [420.0, 420.0], [220.0, 420.0]],
        "homography": None,
        "scale_cm_per_px": DEMO_SCALE_CM_PER_PX,
        "orientation": "cenital_ok",
        "stability": "estable",
        "message": "Modo demo: se simula la detección del marcador ArUco.",
    }
    preprocess = {
        "cenital_image": _demo_cenital_image(),
        "width_cm": DEMO_WIDTH_CM,
        "height_cm": DEMO_HEIGHT_CM,
        "scale_cm_per_px": DEMO_SCALE_CM_PER_PX,
        "total_patches": DEMO_TOTAL_PATCHES,
    }
    filter_res = {
        "implemented": True,
        "model_present": True,
        "total_patches": DEMO_TOTAL_PATCHES,
        "crack_patches": DEMO_CRACK_PATCHES,
        "no_crack_patches": DEMO_TOTAL_PATCHES - DEMO_CRACK_PATCHES,
        "verdict": "GRIETA",
        "confidence": round(DEMO_CRACK_PATCHES / DEMO_TOTAL_PATCHES, 4),
        "patches": [],
        "message": "Modo demo: resultado sintético de ejemplo.",
    }
    return {"aruco": aruco, "preprocess": preprocess, "filter": filter_res}