# Contrato de API — Backend FastAPI

Documento técnico del contrato REST + WebSocket. El **único** contrato que
consume el frontend son los **esquemas Pydantic** de `backend/core/schemas.py`;
la documentación interactiva vive en `http://localhost:8000/docs`.

## Convenciones

- Formato: **JSON** (base64 para imágenes).
- Errores: HTTP estándar con `{"detail": "..."}`.
- `APP_MODE=demo` hace que `/api/analyze` devuelva un reporte sintético
  (ver [`arquitectura.md`](arquitectura.md)).

## Endpoints REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Estado del servicio y del modelo |
| `POST` | `/api/camera/start` | Inicia una sesión de cámara |
| `POST` | `/api/camera/stop` | Detiene una sesión (`?session_id=`) |
| `POST` | `/api/capture` | Registra un frame + sensor en la sesión (`?session_id=`) |
| `POST` | `/api/aruco/detect` | Detecta el marcador ArUco (sección 2) |
| `POST` | `/api/preprocess` | Vista cenital + escala + parches (sección 2) |
| `POST` | `/api/filter` | Filtro binario sobre los parches (sección 3) |
| `POST` | `/api/analyze` | Pipeline completo (secciones 1–3) → `AnalyzeResponse` |

## Esquemas principales (`core/schemas.py`)

### Request de entrada
```jsonc
// CaptureRequest
{
  "image": "<base64 del frame>",
  "sensor": { "rotation": [0.1, -0.2, 0.05], "accel": [0, 0, 9.8] }  // opcional
}
```

### `GET /api/health`
```jsonc
{
  "status": "ok",
  "mode": "demo",          // APP_MODE
  "demo": true,
  "sections": { "1_captura": true, "2_preprocesamiento": true, "3_filtro": true },
  "filter_model": "pending",      // "loaded" | "pending"
  "filter_model_path": "<...>/model/model_binary/filter.tflite"
}
```

### `POST /api/analyze` → `AnalyzeResponse`
```jsonc
{
  "job_id": "uuid",
  "aruco": {
    "detected": true,
    "marker_id": 6,
    "corners": [[x,y], ...],
    "homography": [[...]],
    "scale_cm_per_px": 0.033,
    "orientation": "cenital_ok",
    "stability": "estable",       // "estable" | "inestable"
    "message": null
  },
  "preprocess": {                 // null si no se detectó ArUco
    "cenital_image": "<base64>",  // opcional
    "width_cm": 21.1,
    "height_cm": 21.1,
    "scale_cm_per_px": 0.033,
    "total_patches": 64
  },
  "filter": {                     // null si no se detectó ArUco
    "implemented": true,
    "model_present": true,        // false → verdict "SIN_MODELO"
    "total_patches": 64,
    "crack_patches": 27,
    "no_crack_patches": 37,
    "verdict": "GRIETA",          // "GRIETA" | "NO_GRIETA" | "SIN_MODELO"
    "confidence": 0.42,
    "patches": []
  }
}
```

### `POST /api/filter` → `FilterResult`
Igual que el bloque `filter` de `AnalyzeResponse`, incluyendo `patches` con
`{ patch, probability, label }` si `include_images=true` (default).

## WebSocket

Protocolo común: mensajes JSON `{ "type", "status", "payload" }`.

| Ruta | Uso |
|------|-----|
| `/ws/camera` | Transmisión de frames + sensor en tiempo real; responde `frame_ack` con la estabilidad. |
| `/ws/analyze` | Ejecuta el pipeline y emite `progress` por etapa (`1_captura`, `2_aruco`, `2_preprocesamiento`, `3_filtro`) y luego `result`. |

Ejemplo del flujo `/ws/analyze`:
```jsonc
// cliente → servidor
{ "type": "analyze", "image": "<base64>" }
// servidor → cliente (secuencial)
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "1_captura", "status": 0.1 } }
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "2_aruco", "status": 0.4 } }
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "3_filtro", "status": 0.8 } }
{ "type": "result",   "status": "ok", "payload": { "job_id": "u", "aruco": {}, "preprocess": {}, "filter": {} } }
```

## Frontend — cliente actual

`frontend/src/api/inspect.ts` define `analyzeImage(base64)` que hace
`POST /api/analyze` y devuelve `InspectionReport` (tipos en
`frontend/src/types/inspection.ts`, espejo de los schemas del backend).