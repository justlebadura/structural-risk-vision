"""Sección 3 - Filtro rápido: clasificación binaria grieta/no-grieta.

Corre el modelo MobileNetV2 -> TFLite (Opción A) sobre cada parche para
descartar las zonas sanas y quedarse solo con los parches que probablemente
tienen grieta, minimizando el cómputo de la red de peligro (sprint 2-3).
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from core import config
from core.model_loader import get_filter_model
from services.images import encode_base64_image


def classify_patches(
    patches: List[np.ndarray],
    include_images: bool = True,
    threshold: float = config.FILTER_THRESHOLD,
) -> dict:
    """Clasifica cada parche y agrega el resultado del filtro.

    Si el modelo .tflite aún no está entrenado (sprint 2), se reporta
    model_present=False y verdict="SIN_MODELO" (nunca un mock silencioso).
    """
    model = get_filter_model()

    if not model.present:
        return {
            "implemented": True,
            "model_present": False,
            "total_patches": len(patches),
            "crack_patches": 0,
            "no_crack_patches": 0,
            "verdict": "SIN_MODELO",
            "confidence": None,
            "patches": [],
            "message": "Modelo del filtro no cargado (entrenar peso en sprint 2).",
        }

    results = []
    crack_count = 0
    for p in patches:
        prob = model.predict(p)
        label = "GRIETA" if prob >= threshold else "NO_GRIETA"
        if label == "GRIETA":
            crack_count += 1
        results.append(
            {
                "patch": encode_base64_image(p) if include_images else None,
                "probability": round(prob, 4),
                "label": label,
            }
        )

    no_crack = len(results) - crack_count
    ratio = crack_count / len(results) if results else 0.0
    verdict = "GRIETA" if ratio > 0 else "NO_GRIETA"
    return {
        "implemented": True,
        "model_present": True,
        "total_patches": len(results),
        "crack_patches": crack_count,
        "no_crack_patches": no_crack,
        "verdict": verdict,
        "confidence": round(ratio, 4),
        "patches": results,
    }