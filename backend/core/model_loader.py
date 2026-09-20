"""Cargador de modelos.

En el sprint 1 se define la carga e inferencia del filtro rápido
(MobileNetV2 -> TFLite). El entrenamiento del peso ocurre en el sprint 2;
por eso la carga es tolerante: si el archivo .tflite no existe aún, el
sistema sigue funcionando y el endpoint lo reporta con claridad
(model_present=False), nunca con un mock silencioso.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

from core import config

logger = logging.getLogger("model_loader")


class FilterModel:
    """Interprete TFLite para el filtro binario grieta/no-grieta."""

    def __init__(self) -> None:
        self._interpreter: Optional[Any] = None
        self._input_index: Optional[int] = None
        self._output_index: Optional[int] = None
        self._input_size = config.FILTER_INPUT_SIZE
        self._load()

    def _load(self) -> None:
        if not config.FILTER_MODEL_PATH.exists():
            logger.warning(
                "Modelo de filtro no encontrado en %s. "
                "El peso se entrena en el sprint 2.",
                config.FILTER_MODEL_PATH,
            )
            return
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            logger.warning("tflite-runtime no está instalado; filtro deshabilitado.")
            return

        self._interpreter = tflite.Interpreter(model_path=str(config.FILTER_MODEL_PATH))
        self._interpreter.allocate_tensors()
        self._input_index = self._interpreter.get_input_details()[0]["index"]
        self._output_index = self._interpreter.get_output_details()[0]["index"]
        logger.info("Filtro TFLite cargado desde %s", config.FILTER_MODEL_PATH)

    @property
    def present(self) -> bool:
        return self._interpreter is not None

    def predict(self, patch: np.ndarray) -> float:
        """Devuelve P(grieta) en [0, 1] para un parche RGB de 64x64.

        patch: array float32/uint8 con forma (H, W, 3).
        """
        if not self.present:
            raise RuntimeError("Modelo de filtro no disponible.")

        img = cv2_resize_patch(patch, self._input_size)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)  # (1, 64, 64, 3)

        self._interpreter.set_tensor(self._input_index, img)
        self._interpreter.invoke()
        out = self._interpreter.get_tensor(self._output_index)
        return float(np.squeeze(out))


def cv2_resize_patch(patch: np.ndarray, size: int) -> np.ndarray:
    """Redimensiona un parche usando cv2 si está disponible, si no con numpy."""
    try:
        import cv2

        return cv2.resize(patch, (size, size), interpolation=cv2.INTER_AREA)
    except ImportError:
        # fallback numpy puro (muestreo por bloques)
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