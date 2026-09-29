"""Configuración central del backend.

Definición única de rutas de modelos, parámetros de captura, tamaños de
parches, umbrales y constantes del pipeline de las secciones 1-3 del
Documento de Arquitectura Optimizada.

También carga la variable APP_MODE desde el archivo `.env` ubicado en la
raíz del proyecto (una carpeta por encima de `backend/`).
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Carga del .env en la raíz del proyecto
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


def _load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()

# Modo de ejecución: "demo" (filtro heurístico para debugging) o
# "funcional" (usa el modelo real .tflite). Viene de APP_MODE en .env.
APP_MODE = os.getenv("APP_MODE", "demo").strip().lower()
if APP_MODE not in {"demo", "funcional"}:
    APP_MODE = "demo"

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Entrenamiento del filtro binario
# ---------------------------------------------------------------------------
TRAINING_DATASET_DIR = os.getenv("TRAINING_DATASET_DIR", "")
TRAINING_EPOCHS = int(os.getenv("TRAINING_EPOCHS", "10"))
TRAINING_BATCH_SIZE = int(os.getenv("TRAINING_BATCH_SIZE", "32"))
TRAINING_LR = float(os.getenv("TRAINING_LR", "0.0001"))