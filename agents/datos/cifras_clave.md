# Cifras Clave del Proyecto

> Generado por `evaluate.py` desde [`metricas.json`](metricas.json). **No editar a mano.**

## Modelo binario — set `test` (8000 imágenes: 4000 grieta / 4000 sin grieta)

| Modelo | F1 | Recall | ROC-AUC | Parámetros | TFLite | Latencia |
|--------|----|--------|---------|-----------|--------|----------|
| `unet` | 0.9976 | 0.9980 | 0.9996 | 121,883 | 492.2 KB | 1.49 ms/parche |
| `mobilenetv2` | 0.9974 | 0.9958 | 1.0000 | 411,489 | 1600.3 KB | 0.163 ms/parche |

- **Modelo desplegado**: `unet` (mejor F1 = 0.9976; el más ligero es `unet`, 121,883 parámetros).
- Detalle completo y matrices de confusión: [`../tecnico/stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md).
