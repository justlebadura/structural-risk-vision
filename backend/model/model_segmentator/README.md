# Modelo Segmentador — Segmentación Semántica

Lugar reservado para el **segmentador semántico** (sección de segmentación del
pipeline, **sprint 3**): U-Net / FPN que produce la máscara binaria de la grieta
a partir de la vista cenital (`256×256`).

- **Ruta de pesos esperada**: `segmentator.tflite` en esta carpeta.
- **Configuración**: `config.SEGMENTATOR_MODEL_PATH`.
- **Entrada prevista**: vista cenital corregida (parche/imagen `256×256`).
- **Salida prevista**: máscara binaria `(256, 256)` con la grieta segmentada.

No está integrado aún con los endpoints; el sprint 3 define su contrato de
inferencia (ver `EDA/notebooks/02_pipeline_segmentacion_severidad.ipynb`).