"""Cargador de modelos del filtro rápido (Sección 3).

Según el APP_MODE (`.env` en la raíz):
- **demo** (por defecto): si no hay `.tflite`, se usa un *filtro heurístico* de
  OpenCV (gradiente/textura) que devuelve una probabilidad de grieta plausible.
  Pensado para debugging del pipeline y de la UI, SIN depender de un modelo
  entrenado.
- **funcional**: exige el `.tflite` real (entrenado/desplegado) y corre
  inferencia real. Si el archivo no existe, lo reporta con claridad.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

from core import config

logger = logging.getLogger("model_loader")


class FilterModel:
    """Interprete TFLite (funcional) o heurístico (demo) para grieta/no-grieta."""

    def __init__(self) -> None:
        self.mode = config.APP_MODE
        self._interpreter: Optional[Any] = None
        self._input_index: Optional[int] = None
        self._output_index: Optional[int] = None
        self._input_size = config.FILTER_INPUT_SIZE
        self._demo = False
        self._load_tflite()
        self._demo = not self.present and self.mode == "demo"
        if self._demo:
            logger.info("Modo DEMO activo: usando filtro heurístico (sin .tflite).")
        elif not self.present and self.mode == "funcional":
            logger.warning(
                "Modo FUNCIONAL sin modelo: %s no existe. Entrena/despliega el "
                "modelo o cambia APP_MODE=demo.",
                config.FILTER_MODEL_PATH,
            )

    def _load_tflite(self) -> None:
        if not config.FILTER_MODEL_PATH.exists():
            return
        interp_factory = self._get_interpreter_factory()
        if interp_factory is None:
            logger.warning("No hay runtime TFLite (tflite-runtime ni tensorflow).")
            return
        try:
            self._interpreter = interp_factory(str(config.FILTER_MODEL_PATH))
            self._interpreter.allocate_tensors()
            self._input_index = self._interpreter.get_input_details()[0]["index"]
            self._output_index = self._interpreter.get_output_details()[0]["index"]
            logger.info("Filtro TFLite cargado desde %s", config.FILTER_MODEL_PATH)
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo cargar el .tflite (%s).", exc)
            self._interpreter = None

    @staticmethod
    def _get_interpreter_factory() -> Optional[callable]:
        try:
            import tflite_runtime.interpreter as tflite

            return tflite.Interpreter
        except ImportError:
            pass
        try:
            import tensorflow as tf

            return tf.lite.Interpreter
        except ImportError:
            return None

    @property
    def present(self) -> bool:
        """El modelo responde: TFLite cargado o heurístico en modo demo."""
        return self._interpreter is not None or self._demo

    @property
    def backend(self) -> str:
        if self._interpreter is not None:
            return "tflite"
        if self._demo:
            return "heuristic_demo"
        return "none"

    def predict(self, patch: np.ndarray) -> float:
        """Devuelve P(grieta) en [0, 1] para un parche RGB de 64x64."""
        if self._interpreter is not None:
            return self._predict_tflite(patch)
        if self._demo:
            return self._predict_heuristic(patch)
        raise RuntimeError("No hay modelo de filtro disponible.")

    def _predict_tflite(self, patch: np.ndarray) -> float:
        img = resize_patch(patch, self._input_size)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)  # (1, 64, 64, 3)
        self._interpreter.set_tensor(self._input_index, img)
        self._interpreter.invoke()
        out = self._interpreter.get_tensor(self._output_index)
        return float(np.squeeze(out))

    def _predict_heuristic(self, patch: np.ndarray) -> float:
        """Heurística de debugging: grietas = alta textura/contorno direccional.

        Usa la magnitud del gradiente (Sobel) como proxy de discontinuidad
        superficial. Es determinista y razonablemente sensible a grietas reales.
        """
        import cv2

        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = cv2.magnitude(gx, gy).mean()
        # Mapeo suave: fondo liso (mag baja) -> p(grieta) baja; textura alta -> alta.
        prob = 1.0 / (1.0 + np.exp(-(mag - 30.0) / 18.0))
        return float(np.clip(prob, 0.0, 1.0))


def resize_patch(patch: np.ndarray, size: int) -> np.ndarray:
    """Redimensiona un parche usando cv2 si está disponible, si no con numpy."""
    try:
        import cv2

        return cv2.resize(patch, (size, size), interpolation=cv2.INTER_AREA)
    except ImportError:
        h, w = patch.shape[:2]
        ys = np.linspace(0, h - 1, size, dtype=int)
        xs = np.linspace(0, w - 1, size, dtype=int)
        return patch[np.ix_(ys, xs)]


_filter_model: Optional[FilterModel] = None


def get_filter_model() -> FilterModel:
    global _filter_model
    if _filter_model is None:
        _filter_model = FilterModel()
    return _filter_model


def reload_filter_model() -> FilterModel:
    """Recarga el modelo (tras entrenar/subir un .tflite nuevo)."""
    global _filter_model
    _filter_model = FilterModel()
    return _filter_model