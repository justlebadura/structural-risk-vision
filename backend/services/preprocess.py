"""Sección 2 - Preprocesamiento: vista cenital, escala y división en parches.

Trabaja sobre la imagen ya corregida por ArUco (Sección 2) y la divide en
parches de tamaño fijo (Sección 3) listos para el filtro rápido.
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from core import config
from services.images import encode_base64_image

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


def physical_dimensions(scale_cm_per_px: float, image: np.ndarray) -> dict:
    """Calcula el ancho/alto físicos (cm) de la imagen cenital."""
    if image is None or not scale_cm_per_px:
        return {"width_cm": None, "height_cm": None}
    h, w = image.shape[:2]
    return {
        "width_cm": round(w * scale_cm_per_px, 2),
        "height_cm": round(h * scale_cm_per_px, 2),
    }


def split_patches(image: np.ndarray, size: int = config.PATCH_SIZE) -> List[np.ndarray]:
    """Divide la imagen en parches cuadrados de tamaño `size` (recorte final)."""
    if image is None:
        return []
    h, w = image.shape[:2]
    stride = size
    patches: List[np.ndarray] = []
    for y in range(0, h - size + 1, stride):
        for x in range(0, w - size + 1, stride):
            patches.append(image[y:y + size, x:x + size])
    return patches


def normalize(image: np.ndarray, max_side: int = config.NORM_SIZE) -> Optional[np.ndarray]:
    """Redimensiona la imagen para que su lado mayor sea `max_side`."""
    if image is None or cv2 is None:
        return image
    h, w = image.shape[:2]
    if max(h, w) <= max_side:
        return image
    scale = max_side / float(max(h, w))
    new_size = (int(round(w * scale)), int(round(h * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def preprocess_cenital(
    cenital: np.ndarray,
    scale_cm_per_px: float,
    include_image: bool = True,
) -> dict:
    """Orquesta el preprocesamiento y empaqueta el resultado (Sección 2)."""
    if cenital is None:
        return {
            "cenital_image": None,
            "width_cm": None,
            "height_cm": None,
            "scale_cm_per_px": None,
            "total_patches": 0,
        }

    dims = physical_dimensions(scale_cm_per_px, cenital)
    patches = split_patches(cenital)
    return {
        "cenital_image": encode_base64_image(cenital) if include_image else None,
        "width_cm": dims["width_cm"],
        "height_cm": dims["height_cm"],
        "scale_cm_per_px": scale_cm_per_px,
        "total_patches": len(patches),
    }