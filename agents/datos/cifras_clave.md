# Cifras Clave del Proyecto

> Generado por `evaluate.py` desde [`metricas.json`](metricas.json). **No editar a mano.**

## Modelo binario — set `test` (2000 imágenes: 1000 grieta / 1000 sin grieta)

| Modelo | F1 | Recall | ROC-AUC | Parámetros | TFLite | Latencia |
|--------|----|--------|---------|-----------|--------|----------|
| `unet` | 0.9970 | 0.9980 | 0.9995 | 121,883 | 492.2 KB | 1.412 ms/parche |
| `mobilenetv2` | 0.9970 | 0.9960 | 0.9999 | 411,489 | 1600.3 KB | 0.16 ms/parche |

- **Modelo desplegado**: `unet` (mejor F1 = 0.9970; el más ligero es `unet`, 121,883 parámetros).
- Detalle completo y matrices de confusión: [`../tecnico/stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md).
