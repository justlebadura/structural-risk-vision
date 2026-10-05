# Modelos

Dónde viven los modelos, qué contrato deben cumplir y cómo se integran con el
backend. Los binarios (`*.tflite`) **no se versionan**; se generan en el
sprint 2 y se colocan localmente (ignorados por `.gitignore`).

## Estructura

```
backend/model/
├── model_binary/            # filtro binario grieta/no-grieta (sección 3)
│   ├── binary_model.py      # clase BinaryModel (wrapper TFLite)
│   └── README.md            # contrato detallado de conexión con el backend
└── model_segmentator/       # segmentador semántico (sprint 3, placeholder)
    └── README.md
```

## Modelo binario (`model_binary`)

Clasificador binario que decide si un parche tiene grieta. Se comparan **dos
arquitecturas** y se despliega la más ligera.

| Aspecto | Valor |
|---------|-------|
| Arquitectura desplegada | **U-Net muy ligera** (`Conv1×1 → GAP → Dense(1, sigmoid)`) |
| Pesos | `backend/model/model_binary/filter.tflite` |
| Entrada | Parche RGB `64×64`, normalizado a `[0,1]`, shape `(1, 64, 64, 3)` |
| Salida | `P(grieta) ∈ [0, 1]` (escalar) |
| Umbral | `config.FILTER_THRESHOLD` (`0.5`); `≥ 0.5 → "GRIETA"` |
| Integración | `core/model_loader.get_filter_model()` → `BinaryModel` |
| Baseline alterna | MobileNetV2 (transfer learning, `alpha=0.35`) |

**Resultados** (test METU balanceado): comparación completa, matrices de
confusión y métricas en [`stats_modelo_binario.md`](stats_modelo_binario.md) —
que además incluye la **selección de época** (mejor `val_auc`), si hubo
**early stopping** y el **diagnóstico de under/overfitting** con curvas
train/val. Cifras de titular en [`../datos/cifras_clave.md`](../datos/cifras_clave.md).

- Si `filter.tflite` **no existe**, el backend responde `model_present=false` y
  `verdict="SIN_MODELO"` (nunca un mock silencioso).
- Entrenamiento y evaluación: [`../guias/entrenamiento.md`](../guias/entrenamiento.md).

## Modelo segmentador (`model_segmentator`)

Segmentación semántica (U-Net / FPN) que produce la máscara binaria de la grieta
a partir de la vista cenital `256×256`. Es la **sección 4** del pipeline
(**sprint 3**).

| Aspecto | Valor |
|---------|-------|
| Pesos previstos | `backend/model/model_segmentator/segmentator.tflite` |
| Entrada prevista | Vista cenital corregida `256×256` |
| Salida prevista | Máscara binaria `(256, 256)` |
| Config | `config.SEGMENTATOR_MODEL_PATH` |

Aún **no está integrado** con los endpoints; el sprint 3 define su contrato de
inferencia (referencia: `EDA/notebooks/02_pipeline_segmentacion_severidad.ipynb`).

## Flujo de integración con el backend

```
Frontend ── POST /api/analyze ──► Backend
                                   ├─ aruco.detect()          (services/aruco)
                                   ├─ preprocess.split_patches() (services/preprocess)
                                   ├─ filter.classify_patches() → model_binary
                                   │      └─ BinaryModel.predict(patch) → P(grieta)
                                   └─ responde AnalyzeResponse
Frontend ◄─────────────────────────── reporte
```

## Relación con el EDA

Los umbrales de severidad y el pipeline de medición (transformada de distancia)
se estudian en `EDA/notebooks/`:

- `01_clasificacion_grietas.ipynb` → insumos para el **modelo binario**.
- `02_pipeline_segmentacion_severidad.ipynb` → insumos para el **segmentador** y
  los criterios de severidad (Nivel 1 < 1.0 mm, Nivel 2 1.0–3.0 mm, Nivel 3 > 3.0 mm).