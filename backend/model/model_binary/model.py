"""Definición de modelos del filtro binario grieta/no-grieta.

Dos arquitecturas, ambas ligeras y compatibles con el contrato del backend
(entrada RGB `size×size` en [0,1] → salida escalar `P(grieta)`):

- `build_light_unet_classifier`: **U-Net muy ligera** (encoder–decoder con skip
  connections). El decoder reconstruye detalle espacial y la clasificación se
  obtiene por *global average pooling* + capa densa sigmoide.
- `build_mobilenetv2`: **MobileNetV2 con transfer learning** (pesos ImageNet),
  cabezal GAP + Dense; muy precisa y también apta para móvil.
"""
from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models


def _conv_bn_relu(x, filters: int, name: str):
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False, name=f"{name}_conv1")(x)
    x = layers.BatchNormalization(name=f"{name}_bn1")(x)
    x = layers.Activation("relu", name=f"{name}_relu1")(x)
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False, name=f"{name}_conv2")(x)
    x = layers.BatchNormalization(name=f"{name}_bn2")(x)
    x = layers.Activation("relu", name=f"{name}_relu2")(x)
    return x


def build_light_unet_classifier(input_size: int = 64, filters=(8, 16, 32, 64)) -> tf.keras.Model:
    """U-Net muy ligera adaptada a clasificación binaria.

    Encoder: 4 niveles (Conv-BN-ReLU ×2 + MaxPool). Decoder: 3 niveles con
    `Conv2DTranspose` y skip connections. Cabeza: Conv 1×1 → GAP → Dense(1).
    """
    inputs = layers.Input(shape=(input_size, input_size, 3), name="patch")

    # --- Encoder ---
    skips = []
    x = inputs
    for i, f in enumerate(filters):
        x = _conv_bn_relu(x, f, name=f"enc{i+1}")
        skips.append(x)
        if i < len(filters) - 1:
            x = layers.MaxPooling2D(2, name=f"pool{i+1}")(x)

    # --- Decoder (con skip connections) ---
    for i in range(len(filters) - 2, -1, -1):
        f = filters[i]
        x = layers.Conv2DTranspose(f, 2, strides=2, padding="same", name=f"up{i+1}")(x)
        x = layers.Concatenate(name=f"skip{i+1}")([x, skips[i]])
        x = _conv_bn_relu(x, f, name=f"dec{i+1}")

    # --- Cabeza de clasificación ---
    x = layers.Conv2D(1, 1, padding="same", activation="relu", name="head_conv")(x)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="prob_crack")(x)

    return models.Model(inputs, outputs, name="light_unet_classifier")


def build_mobilenetv2(input_size: int = 64, alpha: float = 0.35, dropout: float = 0.2) -> tf.keras.Model:
    """MobileNetV2 preentrenado en ImageNet con cabezal de clasificación binaria."""
    base = tf.keras.applications.MobileNetV2(
        input_shape=(input_size, input_size, 3),
        alpha=alpha,
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False

    inputs = layers.Input(shape=(input_size, input_size, 3), name="patch")
    # MobileNetV2 espera [-1, 1]; reescalamos desde [0, 1].
    x = layers.Rescaling(scale=2.0, offset=-1.0, name="to_imagenet_range")(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dropout(dropout, name="dropout")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="prob_crack")(x)

    model = models.Model(inputs, outputs, name="mobilenetv2_classifier")
    model._base_model = base  # type: ignore[attr-defined]
    return model


def count_params(model: tf.keras.Model) -> dict:
    trainable = int(sum(tf.keras.backend.count_params(w) for w in model.trainable_weights))
    total = int(model.count_params())
    return {"total": total, "trainable": trainable, "frozen": total - trainable}


def build(name: str, input_size: int = 64) -> tf.keras.Model:
    name = name.lower()
    if name in ("unet", "light_unet", "u-net"):
        return build_light_unet_classifier(input_size)
    if name in ("mobilenetv2", "mobilenet", "mobile"):
        return build_mobilenetv2(input_size)
    raise ValueError(f"Modelo desconocido: {name}")