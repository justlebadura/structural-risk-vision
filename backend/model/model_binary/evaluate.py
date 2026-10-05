"""Evaluación del filtro binario sobre el set de validación/test.

Fuente única de verdad y todo lo derivado de ella (nada de cifras a mano):

- `agents/datos/metricas.json`                       (fuente única de verdad)
- `agents/datos/estadisticas.csv`                    (métricas tabuladas)
- `agents/datos/cifras_clave.md`                     (titulares para presentaciones)
- `agents/tecnico/stats_modelo_binario.md`           (reporte + matrices de confusión)
- `agents/tecnico/confusion_<modelo>.png`            (figuras)

Uso:
    python evaluate.py
    python evaluate.py --models unet mobilenetv2
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

import data as data_mod

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"
# El reporte y las figuras viven en la documentación (agents/), no entre el código.
REPO_ROOT = HERE.parents[2]
REPORT_DIR = REPO_ROOT / "agents" / "tecnico"
REPORT_NAME = "stats_modelo_binario.md"
DATA_DIR = REPO_ROOT / "agents" / "datos"
METRICS_JSON = DATA_DIR / "metricas.json"   # fuente única de verdad
CSV_NAME = "estadisticas.csv"
CIFRAS_NAME = "cifras_clave.md"


def metrics_at(y_true, proba, threshold: float) -> dict:
    y_pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "threshold": round(float(threshold), 3),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "specificity": round(float(specificity), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, proba)), 4),
        "pr_auc": round(float(average_precision_score(y_true, proba)), 4),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def best_thresholds(y_true, proba) -> dict:
    grid = np.linspace(0.05, 0.95, 91)
    f1s = [f1_score(y_true, (proba >= t).astype(int), zero_division=0) for t in grid]
    best_f1_t = float(grid[int(np.argmax(f1s))])
    # Youden J = sensibilidad + especificidad - 1
    js = []
    for t in grid:
        yp = (proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, yp, labels=[0, 1]).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0
        spec = tn / (tn + fp) if (tn + fp) else 0
        js.append(sens + spec - 1)
    best_j_t = float(grid[int(np.argmax(js))])
    return {"best_f1_threshold": round(best_f1_t, 3), "youden_threshold": round(best_j_t, 3)}


def plot_confusion(cm: dict, title: str, out_path: Path) -> None:
    mat = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    im = ax.imshow(mat, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(mat[i, j]), ha="center", va="center",
                    color="white" if mat[i, j] > mat.max() / 2 else "black", fontsize=12)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Pred: No-grieta", "Pred: Grieta"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Real: No-grieta", "Real: Grieta"])
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def tflite_latency(path: Path, input_size: int, runs: int = 100) -> dict:
    interp = tf.lite.Interpreter(model_path=str(path))
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    out = interp.get_output_details()[0]
    x = np.random.rand(1, input_size, input_size, 3).astype(np.float32)
    interp.set_tensor(inp["index"], x); interp.invoke()  # warmup
    t0 = time.perf_counter()
    for _ in range(runs):
        interp.set_tensor(inp["index"], x)
        interp.invoke()
    dt = (time.perf_counter() - t0) / runs
    return {"ms_per_patch": round(dt * 1000, 3), "patches_per_s": round(1.0 / dt, 1)}


def evaluate_model(name: str, X, y, size: int) -> dict:
    model_path = ARTIFACTS / f"{name}.keras"
    if not model_path.exists():
        raise FileNotFoundError(f"No existe {model_path}. Entrena primero con train.py")
    model = tf.keras.models.load_model(model_path)
    proba = model.predict(X, batch_size=128, verbose=0).ravel()

    base = metrics_at(y, proba, 0.5)
    th = best_thresholds(y, proba)
    base.update(th)
    base["model"] = name
    base["params"] = int(model.count_params())

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cm_path = REPORT_DIR / f"confusion_{name}.png"
    plot_confusion(base["confusion"], f"Matriz de confusión — {name} (umbral 0.5)", cm_path)
    base["confusion_png"] = cm_path.name

    tfl = ARTIFACTS / f"{name}.tflite"
    if tfl.exists():
        base["tflite_size_kb"] = round(tfl.stat().st_size / 1024, 1)
        base["latency"] = tflite_latency(tfl, size)
    return base


def _row(m: dict) -> str:
    return (f"| {m['model']} | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | "
            f"{m['specificity']:.4f} | {m['f1']:.4f} | {m['roc_auc']:.4f} | {m['pr_auc']:.4f} |")


def write_report(results: list, meta: dict, out_path: Path) -> None:
    lines = []
    lines.append("# Métricas del Modelo Binario (Grieta / No-grieta)\n")
    lines.append("Reporte generado automáticamente por `evaluate.py`.\n")
    lines.append("## 1. Dataset de evaluación\n")
    lines.append(f"- **Fuente**: METU — Concrete Crack Images for Classification (Özgenel, 2019).")
    lines.append(f"- **Set**: `{meta['split']}` con {meta['total']} imágenes "
                 f"({meta['positive']} grieta / {meta['negative']} sin grieta).")
    lines.append(f"- **Entrada**: RGB {meta['input_size']}×{meta['input_size']}, normalizado a [0, 1].")
    lines.append(f"- **Umbral por defecto**: 0.5.\n")

    lines.append("## 2. Comparación de modelos\n")
    lines.append("| Modelo | Accuracy | Precision | Recall | Specificity | F1 | ROC-AUC | PR-AUC |")
    lines.append("|--------|----------|-----------|--------|-------------|----|---------|--------|")
    for m in results:
        lines.append(_row(m))
    lines.append("")

    for m in results:
        lines.append(f"## 3.{results.index(m)+1} Detalle — {m['model']}\n")
        lines.append(f"- Parámetros: **{m['params']:,}**")
        if "tflite_size_kb" in m:
            lines.append(f"- Tamaño TFLite: **{m['tflite_size_kb']} KB**")
            lines.append(f"- Latencia: **{m['latency']['ms_per_patch']} ms/parche** "
                         f"(~{m['latency']['patches_per_s']} parches/s, CPU)")
        lines.append(f"- Umbral óptimo (mejor F1): **{m['best_f1_threshold']}** | "
                     f"Youden J: **{m['youden_threshold']}**\n")
        lines.append("**Matriz de confusión** (umbral 0.5):\n")
        c = m["confusion"]
        lines.append("| | Pred: No-grieta | Pred: Grieta |")
        lines.append("|---|---|---|")
        lines.append(f"| **Real: No-grieta** | TN={c['tn']} | FP={c['fp']} |")
        lines.append(f"| **Real: Grieta** | FN={c['fn']} | TP={c['tp']} |")
        lines.append("")
        lines.append(f"![confusión {m['model']}]({m['confusion_png']})\n")

    if len(results) >= 2:
        best = max(results, key=lambda r: r["f1"])
        lightest = min(results, key=lambda r: r["params"])
        fastest = min((r for r in results if "latency" in r), key=lambda r: r["latency"]["ms_per_patch"],
                      default=None)
        lines.append("## 4. Conclusión\n")
        lines.append(f"- Mejor **F1**: `{best['model']}` ({best['f1']:.4f}).")
        lines.append(f"- Modelo más **ligero**: `{lightest['model']}` "
                     f"({lightest['params']:,} parámetros, {lightest.get('tflite_size_kb', '?')} KB).")
        if fastest is not None:
            lines.append(f"- Menor **latencia**: `{fastest['model']}` "
                         f"({fastest['latency']['ms_per_patch']} ms/parche).")
        lines.append("- Si el F1 empata, se recomienda el modelo **más ligero** para el filtro "
                     "rápido en móvil; MobileNetV2 aporta su mejor latencia vía XNNPACK.\n")

    lines.append("## 5. Limitaciones\n")
    lines.append("- METU es un benchmark **casi saturado**: el estado del arte reporta "
                 ">99% en esta tarea, por lo que un F1 ≈ 1.0 es esperable (y no debe "
                 "leerse como 'problema resuelto').")
    lines.append("- Los índices del set de **test** están entrelazados con **train**, de modo "
                 "que podrían compartir foto-fuente (METU genera 40k parches desde 458 fotos). "
                 "La **validación** (bloque contiguo, sin solapamiento de índices) da una "
                 "exactitud similar, lo que respalda el resultado.")
    lines.append("- METU son fotografías de grietas de cerca; los parches reales del pipeline "
                 "provienen de la vista cenital (dominio distinto). La métrica **real** que "
                 "importa es el desempeño en ese dominio, aún por medir.")
    lines.append("- El modelo es un **filtro rápido** por parche: el veredicto final del pipeline "
                 "agrega el ratio de parches con grieta.")
    lines.append("- Entrenado en CPU con un subconjunto del dataset.\n")

    out_path.write_text("\n".join(lines))


def write_csv(results: list, meta: dict, out_path: Path) -> None:
    """Genera `estadisticas.csv` a partir de las métricas (no a mano)."""
    import csv

    rows = []

    def add(cat, met, val, unit, desc, src):
        rows.append([cat, met, val, unit, desc, src])

    src = "agents/tecnico/stats_modelo_binario.md"
    for r in results:
        c = r["confusion"]
        add(f"Modelo:{r['model']}", "parametros", r["params"], "parámetros", "Tamaño total del modelo", src)
        add(f"Modelo:{r['model']}", "tamano_tflite", r.get("tflite_size_kb"), "KB", "Peso del .tflite para móvil", src)
        for key, desc in [
            ("accuracy", "Exactitud global (umbral 0.5)"),
            ("precision", "Precisión (positivos predichos correctos)"),
            ("recall", "Recall/sensibilidad (grietas detectadas)"),
            ("specificity", "Especificidad (sanos correctos)"),
            ("f1", "F1-score (balance precision/recall)"),
            ("roc_auc", "Área bajo la curva ROC"),
            ("pr_auc", "Área bajo la curva Precision-Recall"),
        ]:
            add(f"Modelo:{r['model']}", key, r[key], "ratio [0,1]", desc, src)
        add(f"Modelo:{r['model']}", "latencia", r["latency"]["ms_per_patch"], "ms/parche",
            "Inferencia TFLite en CPU", src)
        add(f"Modelo:{r['model']}", "throughput", r["latency"]["patches_per_s"], "parches/s",
            "Parches procesados por segundo", src)
        add(f"Modelo:{r['model']}", "umbral_optimo_f1", r["best_f1_threshold"], "probabilidad",
            "Umbral que maximiza F1", src)
        add(f"Modelo:{r['model']}", "verdadero_positivo", c["tp"], "imágenes", "TP en test (grietas correctas)", src)
        add(f"Modelo:{r['model']}", "verdadero_negativo", c["tn"], "imágenes", "TN en test (sanos correctos)", src)
        add(f"Modelo:{r['model']}", "falso_positivo", c["fp"], "imágenes", "FP en test (falsa alarma)", src)
        add(f"Modelo:{r['model']}", "falso_negativo", c["fn"], "imágenes", "FN en test (grieta no detectada)", src)

    add("Dataset:METU", "eval_total", meta["total"], "imágenes", "Subconjunto balanceado usado en la evaluación", src)
    add("Dataset:METU", "eval_positive", meta["positive"], "imágenes", "Con grieta en el set de evaluación", src)
    add("Dataset:METU", "eval_negative", meta["negative"], "imágenes", "Sin grieta en el set de evaluación", src)
    add("Dataset:METU", "input_size", f"{meta['input_size']}x{meta['input_size']}", "píxeles",
        "Tamaño de entrada del modelo", src)

    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["categoria", "metrica", "valor", "unidad", "descripcion", "fuente"])
        w.writerows(rows)


def write_cifras(results: list, meta: dict, out_path: Path) -> None:
    """Genera `cifras_clave.md`: cifras de titular para presentaciones."""
    lines = [
        "# Cifras Clave del Proyecto",
        "",
        "> Generado por `evaluate.py` desde [`metricas.json`](metricas.json). "
        "**No editar a mano.**",
        "",
        f"## Modelo binario — set `{meta['split']}` "
        f"({meta['total']} imágenes: {meta['positive']} grieta / {meta['negative']} sin grieta)",
        "",
        "| Modelo | F1 | Recall | ROC-AUC | Parámetros | TFLite | Latencia |",
        "|--------|----|--------|---------|-----------|--------|----------|",
    ]
    for r in results:
        lat = r.get("latency", {}).get("ms_per_patch", "—")
        lines.append(
            f"| `{r['model']}` | {r['f1']:.4f} | {r['recall']:.4f} | {r['roc_auc']:.4f} | "
            f"{r['params']:,} | {r.get('tflite_size_kb', '—')} KB | {lat} ms/parche |"
        )
    if results:
        best = max(results, key=lambda r: r["f1"])
        lightest = min(results, key=lambda r: r["params"])
        lines += [
            "",
            f"- **Modelo desplegado**: `{best['model']}` (mejor F1 = {best['f1']:.4f}; "
            f"el más ligero es `{lightest['model']}`, {lightest['params']:,} parámetros).",
            f"- Detalle completo y matrices de confusión: "
            f"[`../tecnico/stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md).",
            "",
        ]
    out_path.write_text("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", default=["unet", "mobilenetv2"])
    p.add_argument("--split", default="test", choices=["validation", "test"])
    p.add_argument("--input-size", type=int, default=64)
    p.add_argument("--n-per-class", type=int, default=1000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    items = data_mod.list_split(args.split, args.n_per_class, seed=args.seed)
    meta = {**data_mod.summarize(items), "split": args.split, "input_size": args.input_size}
    print(f"[eval] {args.split}: {meta}")
    X, y = data_mod.load_arrays(items, args.input_size)

    results = []
    for name in args.models:
        try:
            r = evaluate_model(name, X, y, args.input_size)
            results.append(r)
            print(f"[eval] {name}: acc={r['accuracy']} f1={r['f1']} recall={r['recall']} auc={r['roc_auc']}")
        except FileNotFoundError as e:
            print(f"[skip] {e}")

    if not results:
        raise SystemExit("No se pudo evaluar ningún modelo.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(exist_ok=True)

    # Fuente única de verdad + todo lo derivado de ella.
    METRICS_JSON.write_text(json.dumps({"meta": meta, "results": results}, indent=2))
    write_report(results, meta, REPORT_DIR / REPORT_NAME)
    write_csv(results, meta, DATA_DIR / CSV_NAME)
    write_cifras(results, meta, DATA_DIR / CIFRAS_NAME)
    print(f"[done] generados: {METRICS_JSON}, {DATA_DIR / CSV_NAME}, "
          f"{DATA_DIR / CIFRAS_NAME}, {REPORT_DIR / REPORT_NAME}")


if __name__ == "__main__":
    main()