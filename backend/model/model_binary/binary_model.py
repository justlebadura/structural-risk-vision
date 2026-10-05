"""Modelo binario grieta/no-grieta (MobileNetV2 → TFLite).

Este módulo define el CONTRATO que el modelo binario debe cumplir para que el
backend lo consuma. El backend carga este modelo a través de
`core.model_loader.get_filter_model()` y lo expone a la interfaz mediante los
endpoints REST `/api/filter` y `/api/analyze` (y el WebSocket `/ws`).

## Cómo se conecta con el backend

1. **Pesos**: se espera el archivo `filter.tflite` junto a este módulo
   (en `backend/model/model_binary/`). Se entrena en el sprint 2 a partir de
   los cuadernos de `EDA/notebooks/`.
2. **Entrada**: un parche RGB de `64×64` (config `FILTER_INPUT_SIZE`),
   normalizado a `[0, 1]` y con forma `(1, 64, 64, 3)`.
3. **Salida**: probabilidad de grieta `P(grieta) ∈ [0, 1]` (escalar).
4. **Umbral**: `config.FILTER_THRESHOLD` (0.5). `≥ umbral → "GRIETA"`.
5. El backend clasifica cada parche, agrega el veredicto y se lo devuelve al
   frontend (`FilterResult`). Ver `README.md` de esta carpeta.
"""
from __future__ import annotations

from typing import Any, Optional

import numpy as np

from core import config

logger = __import__("logging").getLogger("model_binary")


class BinaryModel:
    """Interprete TFLite del filtro binario grieta/no-grieta."""

    def __init__(self) -> None:
        self._interpreter: Optional[Any] = None
        self._input_index: Optional[int] = None
        self._output_index: Optional[int] = None
        self._input_size = config.FILTER_INPUT_SIZE
        self._load()

    def _load(self) -> None:
        if not config.FILTER_MODEL_PATH.exists():
            logger.warning(
                "Modelo binario no encontrado en %s. El peso se entrena en el sprint 2.",
                config.FILTER_MODEL_PATH,
            )
            return
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            logger.warning("tflite-runtime no está instalado; filtro binario deshabilitado.")
            return

        self._interpreter = tflite.Interpreter(model_path=str(config.FILTER_MODEL_PATH))
        self._interpreter.allocate_tensors()
        self._input_index = self._interpreter.get_input_details()[0]["index"]
        self._output_index = self._interpreter.get_output_details()[0]["index"]
        logger.info("Filtro binario TFLite cargado desde %s", config.FILTER_MODEL_PATH)

    @property
    def present(self) -> bool:
        return self._interpreter is not None

    def predict(self, patch: np.ndarray) -> float:
        """Devuelve P(grieta) en [0, 1] para un parche RGB de 64x64."""
        if not self.present:
            raise RuntimeError("Modelo binario no disponible.")

        img = resize_patch(patch, self._input_size)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)  # (1, 64, 64, 3)

        self._interpreter.set_tensor(self._input_index, img)
        self._interpreter.invoke()
        out = self._interpreter.get_tensor(self._output_index)
        return float(np.squeeze(out))


def resize_patch(patch: np.ndarray, size: int) -> np.ndarray:
    """Redimensiona un parche usando cv2 si está disponible, si no con numpy."""
    try:
        import cv2

        return cv2.resize(patch, (size, size), interpolation=cv2.INTER_AREA)
    except ImportError:  # pragma: no cover
        h, w = patch.shape[:2]
        ys = np.linspace(0, h - 1, size, dtype=int)
        xs = np.linspace(0, w - 1, size, dtype=int)
        return patch[np.ix_(ys, xs)]