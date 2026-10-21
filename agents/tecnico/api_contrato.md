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
| `POST` | `/api/inclination` | Inclinación aparente del elemento (Canny + Hough) |
| `POST` | `/api/preprocess` | Vista cenital + escala + parches (sección 2) |
| `POST` | `/api/filter` | Filtro binario sobre los parches (sección 3) |
| `POST` | `/api/analyze` | Pipeline completo (secciones 1–3) → `AnalyzeResponse` |

## Esquemas principales (`core/schemas.py`)

### Request de entrada
```jsonc
// CaptureRequest
{
  "image": "<base64 del frame>",
  // Sensor del dispositivo (opcional). rotation = giróscopo (rad/s), accel = acelerómetro (m/s², incluye gravedad)
  "sensor": { "rotation": [0.1, -0.2, 0.05], "accel": [0, 0, 9.8] },
  // Contexto aportado por el usuario (opcional): dónde está la grieta
  "context": { "element": "columna", "location": "columna C3, 1.2 m", "notes": null }
}
```

> `context.element` admite: `columna`, `viga`, `muro`, `losa`, `piso`, `techo`, `otro`.
> El `accel` se usa para clasificar la **superficie** (techo / piso / pared).

### `GET /api/health`
```jsonc
{
  "status": "ok",
  "mode": "demo",          // APP_MODE
  "demo": true,
  "sections": {
    "1_captura": true,
    "2_preprocesamiento": true,
    "2_inclinacion": true,
    "3_filtro": true
  },
  "filter_model": "pending",      // "loaded" | "pending"
  "filter_model_path": "<...>/model/model_binary/filter.tflite"
}
```

### `POST /api/analyze` → `AnalyzeResponse`
```jsonc
{
  "job_id": "uuid",
  "mode": "prod",                 // "demo" | "prod"
  "demo": false,                  // true si el reporte es sintético
  "aruco": {
    "detected": true,
    "marker_id": 6,
    "corners": [[x,y], ...],
    "homography": [[...]],
    "scale_cm_per_px": 0.033,
    "tilt_deg": 4.2,              // inclinación del marcador (grados, sin calibración)
    "roll_deg": 0.0,              // rotación en el plano de la imagen
    "cenital_ok": true,           // tilt <= MAX_TILT_DEG
    "orientation": "cenital_ok",  // "cenital_ok" | "angulo_incorrecto"
    "stability": "estable",       // "estable" | "inestable"
    "message": null
  },
  "preprocess": {                 // null si no se detectó ArUco
    "cenital_image": "<base64>",  // imagen rectificada (fronto-paralela)
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
  },
  "inclination": {
    "detected": true,
    "method": "canny_hough",
    "tilt_deg": 2.9,              // inclinación aparente respecto al eje
    "tilt_signed_deg": 2.9,
    "angle_deg": 92.9,
    "reference": "vertical",      // "vertical" | "horizontal" | "auto"
    "confidence": 0.93,           // proporción de longitud inlier
    "lines_count": 13,
    "inlier_lines": 11,
    "reliable": true,
    "message": "Inclinación estimada con Canny + Hough."
  },
  // Contexto de la inspección (Sección 1)
  "surface": "piso",              // "techo" | "piso" | "pared" | "indeterminado"
  "surface_tilt_deg": 0.0,        // ángulo del dispositivo respecto a la horizontal
  "element": "columna",           // eco del contexto del usuario
  "location": "columna C3, 1.2 m"
}
```

### `POST /api/inclination` → `ElementInclination`

Misma estructura que el bloque `inclination` de `AnalyzeResponse`. La medición
es **aparente respecto al eje de la imagen/marcador**; no es una inclinación
absoluta respecto a la gravedad.

### `POST /api/filter` → `FilterResult`
Igual que el bloque `filter` de `AnalyzeResponse`, incluyendo `patches` con
`{ patch, probability, label }` si `include_images=true` (default).

## WebSocket

Protocolo común: mensajes JSON `{ "type", "status", "payload" }`.

| Ruta | Uso |
|------|-----|
| `/ws/camera` | Transmisión de frames + sensor en tiempo real; responde `frame_ack` con la estabilidad. |
| `/ws/analyze` | Ejecuta el pipeline y emite `progress` por etapa (`1_captura`, `2_aruco`, `2_preprocesamiento`, `2_inclinacion`, `3_filtro`) y luego `result`. |

Ejemplo del flujo `/ws/analyze`:
```jsonc
// cliente → servidor
{ "type": "analyze", "image": "<base64>" }
// servidor → cliente (secuencial)
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "1_captura", "status": 0.1 } }
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "2_aruco", "status": 0.4 } }
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "2_inclinacion", "status": 0.7 } }
{ "type": "progress", "status": "ok", "payload": { "job_id": "u", "step": "3_filtro", "status": 0.8 } }
{ "type": "result",   "status": "ok", "payload": { "job_id": "u", "aruco": {}, "preprocess": {}, "filter": {}, "inclination": {} } }
```

## Frontend — cliente actual

`frontend/src/api/inspect.ts` define `analyzeImage(base64)` que hace
`POST /api/analyze` y devuelve `InspectionReport` (tipos en
`frontend/src/types/inspection.ts`, espejo de los schemas del backend).