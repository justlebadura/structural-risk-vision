"""Utilidades de imagen compartidas entre servicios."""
from __future__ import annotations

import base64
from typing import Optional

import numpy as np


def decode_base64_image(data: str) -> Optional[np.ndarray]:
    """Convierte una imagen base64 (con o sin prefijo data:) en un array BGR."""
    if data.startswith("data:"):
        data = data.split(",", 1)[1]
    try:
        raw = base64.b64decode(data)
    except Exception:
        return None
    arr = np.frombuffer(raw, dtype=np.uint8)
    try:
        import cv2

        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img if img is not None else None
    except ImportError:
        return None


def encode_base64_image(img: np.ndarray, ext: str = ".jpg") -> Optional[str]:
    """Convierte un array BGR a base64 (jpg por defecto)."""
    if img is None:
        return None
    try:
        import cv2

        ok, buf = cv2.imencode(ext, img)
        if not ok:
            return None
        return base64.b64encode(buf.tobytes()).decode("ascii")
    except ImportError:
        return None