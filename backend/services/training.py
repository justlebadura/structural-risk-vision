"""Servicio de entrenamiento del filtro binario (Sección 3).

Gestiona el ciclo de vida del entrenamiento (idle/running/done/error) en
segundo plano. El entrenamiento real usa transfer learning con MobileNetV2 y
exporta `filter.tflite`; si TensorFlow o el dataset no están disponibles,
queda preparado el flujo y se indica cómo proceder (subir modelo o indicar
dataset vía .env).
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Optional

import numpy as np

from core import config

logger = logging.getLogger("training")


class TrainingService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.state = "idle"          # idle | running | done | error
        self.metrics: dict = {}
        self.params: dict = {}
        self.model_path = str(config.FILTER_MODEL_PATH)
        self.message: Optional[str] = None
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self._thread: Optional[threading.Thread] = None
        self._stop = False

    def status(self) -> dict:
        with self._lock:
            return {
                "state": self.state,
                "metrics": self.metrics,
                "params": self.params,
                "model_path": self.model_path,
                "message": self.message,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
            }

    def start(self, params: Optional[dict] = None) -> dict:
        with self._lock:
            if self.state == "running":
                return self.status()
            self.params = params or {}
            self._apply_defaults()
            self.state = "running"
            self.metrics = {}
            self.message = None
            self.started_at = datetime.now().isoformat()
            self.finished_at = None
            self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self.status()

    def stop(self) -> dict:
        with self._lock:
            self._stop = True
            if self.state != "running":
                self.state = "error"
                self.message = "No hay entrenamiento en curso."
            return self.status()

    def _apply_defaults(self) -> None:
        self.params.setdefault("epochs", config.TRAINING_EPOCHS)
        self.params.setdefault("batch_size", config.TRAINING_BATCH_SIZE)
        self.params.setdefault("lr", config.TRAINING_LR)
        self.params.setdefault("dataset_dir", config.TRAINING_DATASET_DIR)

    def _run(self) -> None:
        dataset = self.params.get("dataset_dir")
        try:
            if not dataset:
                raise RuntimeError(
                    "Falta dataset_dir (o TRAINING_DATASET_DIR en .env). "
                    "El entrenamiento se delega al cuaderno; sube el modelo con "
                    "POST /api/model/upload."
                )
            self._train(dataset)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Entrenamiento falló.")
            with self._lock:
                self.state = "error"
                self.message = str(exc)
                self.finished_at = datetime.now().isoformat()

    def _train(self, dataset_dir: str) -> None:
        try:
            import tensorflow as tf
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "tensorflow no está instalado. Ejecuta el entrenamiento en el "
                "cuaderno (EDA) o instala tensorflow y vuelve a intentarlo."
            ) from exc

        # Dataset esperado: dataset_dir/positive/*.jpg  y dataset_dir/negative/*.jpg
        positive = _list_images(dataset_dir, "positive")
        negative = _list_images(dataset_dir, "negative")
        if not positive or not negative:
            raise RuntimeError(
                "Dataset inválido: se esperan carpetas 'positive/' y 'negative/' "
                "con imágenes .jpg/.png en dataset_dir."
            )

        epochs = int(self.params.get("epochs", config.TRAINING_EPOCHS))
        batch_size = int(self.params.get("batch_size", config.TRAINING_BATCH_SIZE))
        lr = float(self.params.get("lr", config.TRAINING_LR))

        x, y = _build_dataset(positive, negative)
        model = _build_mobilenet(lr)
        history = model.fit(
            x, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0
        )

        acc = float(history.history["accuracy"][-1])
        loss = float(history.history["loss"][-1])
        val_acc = float(history.history.get("val_accuracy", [acc])[-1])
        val_loss = float(history.history.get("val_loss", [loss])[-1])

        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        config.FILTER_MODEL_PATH.write_bytes(tflite_model)

        from core.model_loader import reload_filter_model

        reload_filter_model()

        with self._lock:
            self.state = "done"
            self.metrics = {
                "accuracy": round(acc, 4),
                "loss": round(loss, 4),
                "val_accuracy": round(val_acc, 4),
                "val_loss": round(val_loss, 4),
                "epochs": len(history.history["loss"]),
                "params": int(model.count_params()),
            }
            self.message = "Modelo entrenado y exportado a filter.tflite."
            self.finished_at = datetime.now().isoformat()


# ---------------------------------------------------------------------------
# Helpers de entrenamiento
# ---------------------------------------------------------------------------
def _list_images(root: str, split: str) -> list:
    from pathlib import Path

    p = Path(root) / split
    if not p.exists():
        return []
    return [str(f) for f in p.glob("*.jpg")] + [str(f) for f in p.glob("*.jpeg")] + \
        [str(f) for f in p.glob("*.png")]


def _build_dataset(positive: list, negative: list) -> tuple:
    import cv2

    size = config.FILTER_INPUT_SIZE
    imgs, labels = [], []
    for path in positive:
        img = cv2.imread(path)
        if img is None:
            continue
        imgs.append(cv2.resize(img, (size, size)))
        labels.append(1)
    for path in negative:
        img = cv2.imread(path)
        if img is None:
            continue
        imgs.append(cv2.resize(img, (size, size)))
        labels.append(0)
    if not imgs:
        raise RuntimeError("No se pudieron cargar imágenes del dataset.")
    x = np.asarray(imgs, dtype=np.float32) / 255.0
    y = np.asarray(labels, dtype=np.float32)
    return x, y


def _build_mobilenet(lr: float):
    import tensorflow as tf

    base = tf.keras.applications.MobileNetV2(
        input_shape=(config.FILTER_INPUT_SIZE, config.FILTER_INPUT_SIZE, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = False
    model = tf.keras.Sequential(
        [
            base,
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


_training_service: Optional[TrainingService] = None


def get_training_service() -> TrainingService:
    global _training_service
    if _training_service is None:
        _training_service = TrainingService()
    return _training_service