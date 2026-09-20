"""Configuración central del backend.

Definición única de rutas de modelos, parámetros de captura, tamaños de
parches, umbrales y constantes del pipeline de las secciones 1-3 del
Documento de Arquitectura Optimizada.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BACKEND_DIR / "models"
FILTER_MODEL_PATH = MODELS_DIR / "filter.tflite"

# ---------------------------------------------------------------------------
# Captura (Sección 1)
# ---------------------------------------------------------------------------
MARKER_DICT_ID = 6           # Diccionario ArUco por defecto (DICT_5X5_250 = 6)
REAL_MARKER_SIZE_CM = 5.0    # Tamaño real del lado del marcador en cm
MAX_STABILITY_DEVIATION = 0.5  # Desviación tol. del giroscopio para "estable" (rad/s)

# ---------------------------------------------------------------------------
# Preprocesamiento (Sección 2)
# ---------------------------------------------------------------------------
PATCH_SIZE = 64              # Tamaño de parche 64x64 (Sección 3 del doc)
NORM_SIZE = 640              # Máximo lado de la imagen tras normalización

# ---------------------------------------------------------------------------
# Filtro rápido (Sección 3) - MobileNetV2 -> TFLite
# ---------------------------------------------------------------------------
FILTER_INPUT_SIZE = 64
FILTER_THRESHOLD = 0.5       # Probabilidad grieta para clasificar binario