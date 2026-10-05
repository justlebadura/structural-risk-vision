"""Carga de datos del dataset METU (Concrete Crack Images for Classification).

Espera la estructura de splits oficiales:

    EDA/data/metu/
        train/{Positive,Negative}/*.jpg
        validation/{Positive,Negative}/*.jpg
        test/{Positive,Negative}/*.jpg

La ruta se puede anular con la variable de entorno `METU_DATA_DIR`.

El preprocesamiento es IDÉNTICO al de inferencia (`binary_model.BinaryModel`):
resize a `size×size`, RGB y normalización a `[0, 1]`. Así el modelo entrenado
recibe la misma distribución que verá en el backend.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np

# Repo root = .../backend/model/model_binary -> subir 4 niveles
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = _REPO_ROOT / "EDA" / "data" / "metu"

CLASS_DIRS = {"Positive": 1, "Negative": 0}
SPLITS = ("train", "validation", "test")


def data_dir() -> Path:
    return Path(os.environ.get("METU_DATA_DIR", str(DEFAULT_DATA_DIR)))


def list_split(split: str, n_per_class: int | None = None, seed: int = 42) -> List[Tuple[Path, int]]:
    """Devuelve [(ruta, etiqueta)] de un split, opcionalmente submuestreado.

    El submuestreo es balanceado (n por clase) y reproducible por `seed`.
    """
    base = data_dir() / split
    if not base.exists():
        raise FileNotFoundError(
            f"No se encontró el split '{split}' en {base}. "
            "Descarga METU o define METU_DATA_DIR."
        )
    rng = np.random.default_rng(seed)
    items: List[Tuple[Path, int]] = []
    for cname, label in CLASS_DIRS.items():
        files = sorted((base / cname).glob("*.jpg")) + sorted((base / cname).glob("*.png"))
        if n_per_class is not None and len(files) > n_per_class:
            idx = rng.choice(len(files), size=n_per_class, replace=False)
            files = [files[i] for i in sorted(idx)]
        items.extend((p, label) for p in files)
    rng.shuffle(items)
    return items


def load_image(path: Path | str, size: int = 64) -> np.ndarray:
    """Carga una imagen como float32 RGB normalizada a [0,1] y tamaño size×size."""
    import cv2

    img = cv2.imread(str(path), cv2.IMREAD_COLOR)  # BGR
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img.shape[0] != size or img.shape[1] != size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    return img.astype(np.float32) / 255.0


def load_arrays(items: Sequence[Tuple[Path, int]], size: int = 64) -> Tuple[np.ndarray, np.ndarray]:
    """Carga una lista de items a tensores (X, y)."""
    X = np.zeros((len(items), size, size, 3), dtype=np.float32)
    y = np.zeros((len(items),), dtype=np.float32)
    for i, (p, label) in enumerate(items):
        X[i] = load_image(p, size)
        y[i] = float(label)
    return X, y


def _augment(image, label):
    """Augmentación geométrica + fotométrica (coherente con las grietas)."""
    import tensorflow as tf

    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    k = tf.random.uniform([], 0, 4, dtype=tf.int32)
    image = tf.image.rot90(image, k)
    image = tf.image.random_brightness(image, max_delta=0.12)
    image = tf.image.random_contrast(image, lower=0.85, upper=1.15)
    image = tf.clip_by_value(image, 0.0, 1.0)
    return image, label


def build_dataset(
    items: Sequence[Tuple[Path, int]],
    size: int = 64,
    batch: int = 64,
    augment: bool = False,
    shuffle: bool = False,
    seed: int = 42,
):
    """Construye un `tf.data.Dataset` a partir de los items (ruta, etiqueta)."""
    import tensorflow as tf

    paths = [str(p) for p, _ in items]
    labels = [float(l) for _, l in items]

    def _load(path, label):
        img = tf.io.read_file(path)
        img = tf.io.decode_image(img, channels=3, expand_animations=False)
        img = tf.image.resize(img, [size, size], method="area")
        img = tf.cast(img, tf.float32) / 255.0
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), seed=seed, reshuffle_each_iteration=True)
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    if augment:
        ds = ds.map(_augment, num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(batch).prefetch(tf.data.AUTOTUNE)


def summarize(items: Sequence[Tuple[Path, int]]) -> dict:
    labels = np.array([l for _, l in items])
    return {
        "total": int(len(labels)),
        "positive": int((labels == 1).sum()),
        "negative": int((labels == 0).sum()),
    }