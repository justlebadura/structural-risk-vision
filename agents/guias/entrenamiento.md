# Entrenamiento del Modelo Binario

Guía para entrenar y evaluar el filtro binario de grietas
(`backend/model/model_binary/`). Para el contrato con el backend y la
arquitectura, ver [`../tecnico/modelos.md`](../tecnico/modelos.md).

## Requisitos

```bash
cd backend/model/model_binary
pip install -r requirements-train.txt   # tensorflow, scikit-learn, matplotlib, opencv
```

## Datos

Dataset **METU — Concrete Crack Images for Classification** (Özgenel, 2019) en
`EDA/data/metu/` (estructura en [`../datos/datasets.md`](../datos/datasets.md)).
La ruta se puede anular con la variable de entorno `METU_DATA_DIR`.

El preprocesamiento de entrenamiento (`data.py`) es **idéntico** al de inferencia
(`binary_model.BinaryModel`): resize 64×64 + RGB + `/255`.

## Entrenar

```bash
python train.py --model unet --epochs 25 --deploy      # U-Net ligera + copia a filter.tflite
python train.py --model mobilenetv2 --epochs 12 --fine-tune-epochs 6
```

- `--deploy` copia el `.tflite` resultante a `backend/model/model_binary/filter.tflite`
  (el archivo que carga el backend).
- `--n-per-class` / `--n-val-per-class` controlan el submuestreo balanceado
  (por defecto 2000 / 1000, entrenamiento viable en CPU).

## Evaluar

```bash
python evaluate.py --split test --n-per-class 1000
```

Genera el reporte de métricas en
[`../tecnico/stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md) y
`artifacts/metrics.json` + matrices de confusión.

## Archivos del modelo

| Archivo | Rol |
|---------|-----|
| `data.py` | Carga METU, submuestreo balanceado, `tf.data` + augmentación. |
| `model.py` | `build_light_unet_classifier()` y `build_mobilenetv2()`. |
| `train.py` | Entrena y exporta a TFLite (`artifacts/<model>.tflite`). |
| `evaluate.py` | Métricas en test + genera el reporte de stats. |
| `binary_model.py` | Carga TFLite en el backend (`BinaryModel`). |
| `artifacts/` | Salidas de entrenamiento (`.keras`, `.tflite`, figuras) — ignoradas por git. |

## Notas

- El `.tflite` **no se versiona**; se genera con `train.py`.
- En `APP_MODE=demo` el pipeline devuelve un reporte sintético (no usa el modelo).
- El modelo es un **filtro rápido por parche**; el veredicto final agrega el
  ratio de parches con grieta.