"""Configuración central del backend.

Definición única de rutas de modelos, parámetros de captura, tamaños de
parches, umbrales y constantes del pipeline de las secciones 1-3 del
Documento de Arquitectura Optimizada.

Los valores de entorno se cargan desde el `.env` de la RAIZ del repositorio
(ver `.env.example` en la raíz). `APP_MODE` controla el modo de ejecución:

- `demo`: el endpoint `/api/analyze` devuelve un reporte sintético de ejemplo
  (sin requerir marcador ArUco ni modelo entrenado) para validar el frontend.
- `prod`/cualquier otro: se ejecuta el pipeline real (ArUco + preprocesamiento
  + filtro TFLite). El filtro reporta `model_present=False` si el peso no
  existe aún (se entrena en el sprint 2); nunca un mock silencioso.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent

# Carga el `.env` de la RAIZ del repositorio (configuración única para todo el
# proyecto, no un .env propio de backend/). No sobrescribe variables ya definidas.
load_dotenv(REPO_ROOT / ".env")


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    return value.strip() if value else default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name) or default)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Modo de ejecución y servidor
# ---------------------------------------------------------------------------
APP_MODE = _env_str("APP_MODE", "demo").lower()          # "demo" | "prod" | ...
IS_DEMO = APP_MODE == "demo"
API_HOST = _env_str("API_HOST", "0.0.0.0")
API_PORT = _env_int("API_PORT", 8000)
LOG_LEVEL = _env_str("LOG_LEVEL", "info")

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
MODELS_DIR = BACKEND_DIR / "model"                       # contenedor de modelos
BINARY_MODEL_DIR = MODELS_DIR / "model_binary"           # filtro binario (sección 3)
SEGMENTATOR_MODEL_DIR = MODELS_DIR / "model_segmentator" # segmentador semántico (sprint 3)

FILTER_MODEL_PATH = BINARY_MODEL_DIR / "filter.tflite"
SEGMENTATOR_MODEL_PATH = SEGMENTATOR_MODEL_DIR / "segmentator.tflite"

# ---------------------------------------------------------------------------
# Captura (Sección 1)
# ---------------------------------------------------------------------------
MARKER_DICT_ID = 6           # Diccionario ArUco por defecto (DICT_5X5_250 = 6)
REAL_MARKER_SIZE_CM = 5.0    # Tamaño real del lado del marcador en cm
MAX_STABILITY_DEVIATION = 0.5  # Desviación tol. del giroscopio para "estable" (rad/s)

# Orientación de la superficie a partir del acelerómetro (gravedad en el marco del dispositivo).
# |az| dominante → superficie horizontal; |az| pequeño → vertical (pared).
SURFACE_HORIZONTAL_AZ = 0.7  # |az| normalizado > este valor → techo/piso
SURFACE_VERTICAL_AZ = 0.3    # |az| normalizado < este valor → pared

# Ángulo máximo de inclinación del marcador para considerar la captura "cenital".
MAX_TILT_DEG = 35.0

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