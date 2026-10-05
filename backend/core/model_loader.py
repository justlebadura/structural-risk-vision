"""Cargador de modelos.

Puente entre el backend y los modelos en `backend/model/`:

- `model_binary`  → filtro binario grieta/no-grieta (sección 3). Se carga desde
  `model/model_binary/binary_model.py` (`BinaryModel`).
- `model_segmentator` → segmentador semántico (sprint 3), aún no integrado.

La carga es tolerante: si el `.tflite` no existe aún (el peso se entrena en el
sprint 2), el sistema sigue funcionando y el endpoint lo reporta con claridad
(`model_present=False`, `verdict="SIN_MODELO"`), nunca un mock silencioso.
"""
from __future__ import annotations

from typing import Optional

from model.model_binary.binary_model import BinaryModel


_filter_model: Optional[BinaryModel] = None


def get_filter_model() -> BinaryModel:
    """Singleton del modelo binario utilizado por el servicio de filtro."""
    global _filter_model
    if _filter_model is None:
        _filter_model = BinaryModel()
    return _filter_model