# Modelo Binario — Grieta / No-grieta

Clasificador binario (`MobileNetV2 → TFLite`) que decide si un parche de imagen
contiene grieta. Es la **sección 3** del pipeline (filtro rápido).

Este documento explica **qué debe hacer el modelo para conectarse al backend**.

## Flujo de comunicación

```
Frontend (app móvil)
   │  POST /api/analyze   (imagen en base64 + sensor)
   ▼
Backend (FastAPI)
   ├─ aruco.detect()          → Sección 2 (ArUco + homografía)
   ├─ preprocess.split_patches()  → divide la vista cenital en parches 64×64
   ├─ filter.classify_patches()   → usa ESTE modelo binario
   │     │
   │     └─ BinaryModel.predict(patch)  → P(grieta) ∈ [0,1]
   │
   └─ responde FilterResult / AnalyzeResponse
   ▼
Frontend muestra el reporte
```

El modelo se carga en el backend vía `core/model_loader.get_filter_model()`,
que instancia la clase `BinaryModel` definida en `binary_model.py`.

## Contrato que debe cumplir el modelo

| Aspecto | Valor |
|---------|-------|
| Archivo de pesos | `filter.tflite` (en esta misma carpeta `model/model_binary/`) |
| Arquitectura | MobileNetV2 (transfer learning) exportada a TFLite |
| Entrada | Parche RGB de `64×64`, normalizado a `[0, 1]`, shape `(1, 64, 64, 3)` |
| Salida | Probabilidad `P(grieta) ∈ [0, 1]` (escalar) |
| Umbral de decisión | `config.FILTER_THRESHOLD` (`0.5`); `≥ 0.5 → "GRIETA"` |
| Implementación de referencia | `binary_model.py` (clase `BinaryModel`) |

### Pasos para conectar el modelo

1. **Entrenar** el clasificador (ver `EDA/notebooks/01_clasificacion_grietas.ipynb`)
   y exportar a TFLite.
2. **Colocar** el archivo resultante en esta carpeta como `filter.tflite`.
3. **Verificar** la firma de entrada/salida del `.tflite` (64×64×3 → 1 logit).
   Si la arquitectura cambia, ajustar `binary_model.py` (índices de tensores y
   preprocesamiento) para que coincida con el contrato de arriba.
4. **Probar** con los endpoints del backend:
   - `GET /api/health` → `filter_model: "loaded"`.
   - `POST /api/filter` → devuelve el `FilterResult` con los parches clasificados.
   - `POST /api/analyze` → pipeline completo para el frontend.
5. El backend **no mockea**: si el `.tflite` no existe, responde
   `model_present=false` y `verdict="SIN_MODELO"`.

## Endpoints expuestos por el backend (contrato con el frontend)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/analyze` | Pipeline completo (ArUco + preprocesamiento + filtro binario) |
| `POST` | `/api/filter` | Solo el filtro binario sobre los parches |
| `POST` | `/api/aruco/detect` | Detección de ArUco (sección 2) |
| `POST` | `/api/preprocess` | Vista cenital + escala + parches (sección 2) |
| `GET` | `/api/health` | Estado del servicio y del modelo |

El contrato de respuesta (schemas) está en `backend/core/schemas.py`. La
documentación interactiva vive en `http://localhost:8000/docs`.

## Nota

El peso se entrena en el **sprint 2**; por ahora el backend corre en
`APP_MODE=demo` (reporte sintético) y el filtro responde `SIN_MODELO` si se
ejecuta en modo `prod` sin el `.tflite`.