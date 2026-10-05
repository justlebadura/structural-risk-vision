"""Entrenamiento del filtro binario y exportación a TFLite.

Uso:
    python train.py --model unet
    python train.py --model mobilenetv2

Genera:
    artifacts/<model>.keras            modelo entrenado
    artifacts/<model>_history.json     historial de entrenamiento
    artifacts/<model>.tflite           versión TFLite
    filter.tflite                      (si --deploy) listo para el backend

El preprocesamiento de entrenamiento coincide con el de inferencia
(`binary_model.BinaryModel`): RGB `size×size` normalizado a [0, 1].
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import tensorflow as tf

import data as data_mod
import model as model_mod

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"


def _compile(model, lr: float):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )


def export_tflite(model, out_path: Path, quantize: bool = False) -> bytes:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_bytes = converter.convert()
    out_path.write_bytes(tflite_bytes)
    return tflite_bytes


def verify_tflite(path: Path, input_size: int) -> dict:
    interp = tf.lite.Interpreter(model_path=str(path))
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    out = interp.get_output_details()[0]
    # smoke test
    sample = np.zeros((1, input_size, input_size, 3), dtype=np.float32)
    interp.set_tensor(inp["index"], sample)
    interp.invoke()
    pred = interp.get_tensor(out["index"])
    return {
        "input_shape": [int(v) for v in inp["shape"]],
        "input_dtype": str(inp["dtype"].__name__),
        "output_shape": [int(v) for v in out["shape"]],
        "output_dtype": str(out["dtype"].__name__),
        "smoke_pred": float(np.squeeze(pred)),
    }


def train(args) -> dict:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    size = args.input_size

    train_items = data_mod.list_split("train", args.n_per_class, seed=args.seed)
    val_items = data_mod.list_split("validation", args.n_val_per_class, seed=args.seed)
    print(f"[data] train={data_mod.summarize(train_items)} val={data_mod.summarize(val_items)}")

    train_ds = data_mod.build_dataset(train_items, size, args.batch, augment=True, shuffle=True, seed=args.seed)
    val_ds = data_mod.build_dataset(val_items, size, args.batch, augment=False)

    model = model_mod.build(args.model, size)
    params = model_mod.count_params(model)
    print(f"[model] {args.model} params={params}")

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_auc", mode="max", patience=6, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5),
        tf.keras.callbacks.ModelCheckpoint(str(ARTIFACTS / f"{args.model}.keras"), monitor="val_auc",
                                            mode="max", save_best_only=True),
    ]

    history = {}
    t0 = time.time()

    if args.model.startswith("mobile") and getattr(model, "_base_model", None) is not None:
        base = model._base_model
        # Fase 1: cabezal con base congelada
        base.trainable = False
        _compile(model, args.lr)
        h1 = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks, verbose=2)
        # Fase 2: fine-tuning de las capas superiores
        base.trainable = True
        for layer in base.layers[:-args.fine_tune_layers]:
            layer.trainable = False
        _compile(model, args.lr / 10)
        h2 = model.fit(train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs, callbacks=callbacks, verbose=2)
        history = {k: h1.history[k] + h2.history[k] for k in h1.history}
    else:
        _compile(model, args.lr)
        h = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks, verbose=2)
        history = h.history

    elapsed = time.time() - t0

    model.save(ARTIFACTS / f"{args.model}.keras")
    history = {k: [float(v) for v in vals] for k, vals in history.items()}
    (ARTIFACTS / f"{args.model}_history.json").write_text(json.dumps(history, indent=2))

    tflite_path = ARTIFACTS / f"{args.model}.tflite"
    tflite_bytes = export_tflite(model, tflite_path, quantize=args.quantize)
    sig = verify_tflite(tflite_path, size)

    if args.deploy:
        deploy_path = HERE / "filter.tflite"
        deploy_path.write_bytes(tflite_bytes)
        print(f"[deploy] filter.tflite escrito ({len(tflite_bytes)/1024:.1f} KB)")

    result = {
        "model": args.model,
        "input_size": size,
        "params": params,
        "epochs_run": len(history.get("loss", [])),
        "train_seconds": round(elapsed, 1),
        "history": history,
        "tflite": {
            "path": str(tflite_path),
            "size_kb": round(len(tflite_bytes) / 1024, 1),
            **sig,
        },
    }
    (ARTIFACTS / f"{args.model}_train.json").write_text(json.dumps(result, indent=2))
    print(f"[done] {args.model}: {result['epochs_run']} épocas en {elapsed:.1f}s | "
          f"tflite {result['tflite']['size_kb']} KB | sig {sig}")
    return result


def main():
    p = argparse.ArgumentParser(description="Entrena el filtro binario de grietas.")
    p.add_argument("--model", default="unet", choices=["unet", "mobilenetv2"])
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--fine-tune-epochs", type=int, default=8)
    p.add_argument("--fine-tune-layers", type=int, default=30)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--input-size", type=int, default=64)
    p.add_argument("--n-per-class", type=int, default=2000, help="imágenes por clase en train (None=todas)")
    p.add_argument("--n-val-per-class", type=int, default=1000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--quantize", action="store_true", help="dynamic-range quantization")
    p.add_argument("--deploy", action="store_true", help="copiar a filter.tflite")
    args = p.parse_args()
    train(args)


if __name__ == "__main__":
    main()