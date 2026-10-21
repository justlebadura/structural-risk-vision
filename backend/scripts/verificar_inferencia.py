"""Verifica que el backend esté listo para ejecutar inferencia real.

Comprueba que exista `filter.tflite`, que el modelo TFLite cargue y que pueda
producir una probabilidad sobre una imagen real de METU.

Uso:
    python backend/scripts/verificar_inferencia.py
    python backend/scripts/verificar_inferencia.py --image ruta/a/foto.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core import config  # noqa: E402
from core.model_loader import get_filter_model  # noqa: E402
from model.model_binary.data import list_split  # noqa: E402


def _default_image() -> Path:
    items = list_split("test", n_per_class=1, seed=42)
    return next(path for path, label in items if label == 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica el modelo de inferencia.")
    parser.add_argument("--image", type=Path, default=None, help="Imagen a usar.")
    args = parser.parse_args()

    image_path = args.image or _default_image()
    image = cv2.imread(str(image_path))
    if image is None:
        print(json.dumps({"ready": False, "error": f"No se pudo leer {image_path}"}))
        return 1

    model = get_filter_model()
    report = {
        "ready": bool(model.present),
        "mode": config.APP_MODE,
        "filter_model_path": str(config.FILTER_MODEL_PATH),
        "filter_model_present": config.FILTER_MODEL_PATH.exists(),
        "model_loaded": bool(model.present),
        "image": str(image_path),
    }
    if not model.present:
        report["error"] = (
            "Modelo no cargado. Coloca filter.tflite en "
            f"{config.FILTER_MODEL_PATH} o entrena con train.py --deploy."
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    patch = cv2.resize(image, (config.FILTER_INPUT_SIZE, config.FILTER_INPUT_SIZE))
    patch = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB)
    probability = model.predict(patch)
    report.update(
        {
            "probability": round(float(probability), 4),
            "threshold": config.FILTER_THRESHOLD,
            "verdict": "GRIETA" if probability >= config.FILTER_THRESHOLD else "NO_GRIETA",
        }
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
