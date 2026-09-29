# Backend — Contrato de API y Arquitectura (Sprint 1)

**Proyecto:** Structural Risk Vision — Detección de grietas, inclinación y riesgo en edificaciones.
**Universidad Industrial de Santander · Ingeniería en Inteligencia Artificial · Algoritmos y Programación 2026-2**

> Este documento es el **único contrato** entre el backend y el frontend. El frontend **no toca** `backend/`:
> consume exclusivamente el OpenAPI que el backend expone en `/docs` (Swagger) y `/redoc`.

---

## 1. Alcance del Sprint 1

Se implementan las **secciones 1 a 3** del *Documento de Arquitectura Optimizada*:

| Sección | Nombre | Estado |
| :-- | :-- | :-- |
| **1** | Captura (Marcador ArUco + guía por giróscopo) | ✅ Implementado |
| **2** | Preprocesamiento (corrección de perspectiva y escala real) | ✅ Implementado |
| **3** | Filtro rápido (clasificación binaria grieta/no-grieta) | ✅ Implementado (módulo de inferencia) |
| 4-9 | Segmentación, distancia, fusión multicanal, multiclase, Grad-CAM, riesgo | ⏭️ Sprint 2-3 |

> **Nota sobre el filtro (sección 3):** la *inferencia* está implementada (MobileNetV2 → TFLite).
> El **entrenamiento del peso** ocurre en el Sprint 2. Hasta entonces `/api/filter` y `/api/analyze`
> responden `verdict: "SIN_MODELO"` de forma explícita (nunca un mock silencioso).

---

## 2. Arquitectura

```
┌─────────────────────┐          ┌────────────────────────────────────────────┐
│      FRONTEND       │  HTTP/WS  │                BACKEND (FastAPI)          │
│  (otra persona)     │◄─────────►│  backend/                                 │
│  · cámara           │  /api +   │    app.py            entrypoint + CORS    │
│  · giróscopo/sensor │  /ws      │    core/config.py     rutas y umbrales    │
│  · captura y envío  │           │    core/schemas.py    contrato Pydantic   │
│  de frames          │           │    core/model_loader.py  carga .tflite    │
└─────────────────────┘           │    services/                               │
                                  │      camera.py      (Sección 1)            │
  La cámara y el sensor viven     │      aruco.py       (Sección 2)            │
  en el DISPOSITIVO del usuario.  │      preprocess.py  (Sección 2)            │
  El backend solo procesa.        │      filter.py      (Sección 3)            │
                                  │    api/router.py    (endpoints REST)       │
                                  │    api/ws.py        (endpoints WebSocket)  │
                                  │    models/filter.tflite  (peso, sprint 2)  │
                                  └────────────────────────────────────────────┘
```

**Flujo del pipeline (secciones 1-3):**
1. **Captura** → el cliente abre la cámara y transmite frames + datos de sensor por `/ws/camera`.
   El backend evalúa la estabilidad (magnitud de rotación del giróscopo).
2. **ArUco** → detecta el marcador, calcula la **homografía** (vista cenital) y la **escala cm/píxel**
   usando el tamaño real conocido del marcador.
3. **Preprocesamiento** → aplica la vista cenital y divide en **parches 64×64**.
4. **Filtro rápido** → cada parche pasa por el modelo binario; se quedan los parches con grieta y se
   descartan los sanos (optimiza el cómputo de la red de peligro del sprint 2-3).

---

## 3. Cómo levantar y probar

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# --host 0.0.0.0 expone la API a la red local (necesario para la app móvil)
uvicorn app:app --host 0.0.0.0 --port 8000
```

- Documentación interactiva: http://localhost:8000/docs
- Esquema JSON del contrato: http://localhost:8000/openapi.json

---

## 4. Contrato REST

Todas las rutas bajo `/api`. Las imágenes se envían como **base64** en el cuerpo JSON
(objeto `CaptureRequest`).

### `CaptureRequest` (cuerpo común de varios endpoints)
```json
{
  "image": "<imagen en base64>",
  "sensor": {
    "rotation": [0.1, 0.0, 0.0],
    "accel": [0.0, 0.0, 9.8]
  }
}
```

### Tabla de endpoints

| Método | Ruta | Función | Requiere cámara? |
| :-- | :-- | :-- | :-- |
| `GET` | `/api/health` | Estado del servicio y del modelo | No |
| `POST` | `/api/camera/start` | Inicia sesión de captura | No |
| `POST` | `/api/camera/stop` | Cierra sesión (`?session_id=`) | No |
| `POST` | `/api/capture` | Registra frame + sensor en la sesión (`?session_id=`) | Sí |
| `POST` | `/api/aruco/detect` | Detecta ArUco, homografía y escala | No |
| `POST` | `/api/preprocess` | Vista cenital + parches | No |
| `POST` | `/api/filter` | Clasificación binaria por parches | No |
| `POST` | `/api/analyze` | **Pipeline completo 1→3** en un solo call |
| `GET` | `/api/model/status` | Estado y backend del filtro |
| `POST` | `/api/model/upload` | Subir `.tflite` entrenado |
| `GET` | `/api/training/status` | Estado del entrenamiento |
| `POST` | `/api/training/start` | Iniciar entrenamiento |
| `POST` | `/api/training/stop` | Detener entrenamiento | No |

### Ejemplos de respuesta

**`GET /api/health`**
```json
{
  "status": "ok",
  "sections": { "1_captura": true, "2_preprocesamiento": true, "3_filtro": true },
  "filter_model": "pending",
  "filter_model_path": "backend/models/filter.tflite"
}
```

**`POST /api/aruco/detect`**
```json
{
  "detected": true,
  "marker_id": 42,
  "corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]],
  "homography": [[...]],
  "scale_cm_per_px": 0.0251,
  "orientation": "cenital_ok",
  "stability": "estable",
  "message": "Marcador detectado y escala calibrada."
}
```

**`POST /api/analyze`** (encadena 1→3)
```json
{
  "job_id": "uuid",
  "aruco": { "detected": true, "scale_cm_per_px": 0.0251, "..." : "..." },
  "preprocess": { "cenital_image": "<base64>", "width_cm": 16.08, "height_cm": 16.08, "total_patches": 100 },
  "filter": {
    "implemented": true,
    "model_present": false,
    "total_patches": 100,
    "crack_patches": 0,
    "no_crack_patches": 0,
    "verdict": "SIN_MODELO",
    "confidence": null,
    "patches": []
  }
}
```

> El `verdict` del filtro ahora depende del **APP_MODE** (ver sección de modos):
> - `demo` → `verdict: "GRIETA" | "NO_GRIETA"` con `backend: "heuristic_demo"`.
> - `funcional` con modelo → `verdict` real con `backend: "tflite"`.
> - `funcional` sin modelo → `verdict: "SIN_MODELO"` con `backend: "none"` (claro, no falla).

---

## 4b. Modos de ejecución (`APP_MODE` en `.env`)

El backend lee `APP_MODE` desde el archivo `.env` en la **raíz del proyecto**:

| Valor | Comportamiento del filtro (Sección 3) |
| :-- | :-- |
| `demo` (por defecto) | Filtro **heurístico** (gradiente/textura, OpenCV). Sin modelo, listo para debugging de UI y pipeline. |
| `funcional` | Inferencia real con `backend/models/filter.tflite`. |

Copia `.env.example` a `.env` para ajustarlo. En `funcional` sin `.tflite`, el
backend reporta `backend: "none"` y `verdict: "SIN_MODELO"` de forma explícita.

## 4c. Endpoints de modelo y entrenamiento

| Método | Ruta | Función |
| :-- | :-- | :-- |
| `GET` | `/api/model/status` | Estado y backend del filtro (`mode`, `backend`, `size_bytes`) |
| `POST` | `/api/model/upload` | Sube un `.tflite` entrenado (multipart `file`) y lo recarga |
| `GET` | `/api/training/status` | Estado del entrenamiento (`idle/running/done/error`) + métricas |
| `POST` | `/api/training/start` | Inicia entrenamiento en segundo plano (opcional `TrainingConfig`) |
| `POST` | `/api/training/stop` | Detiene el entrenamiento en curso |

**`POST /api/training/start`** body (opcional):
```json
{ "dataset_dir": "/ruta/a/positive-y-negative", "epochs": 10, "batch_size": 32, "lr": 0.0001 }
```
El dataset debe contener `positive/*.jpg` y `negative/*.jpg`. Entrena MobileNetV2
(transfer learning), exporta `filter.tflite` y lo recarga. Si falta el dataset o
TensorFlow, el estado pasa a `error` con un mensaje claro.

---

## 5. Contrato WebSocket

Protocolo común de mensajes: `{ "type": "...", "status": "ok|error|...", "payload": {...} }`.

### `/ws/camera` — transmisión de frames en tiempo real
Cliente → servidor:
```json
{ "type": "frame", "image": "<base64>", "sensor": { "rotation": [0.1, 0.0, 0.0] } }
```
Servidor → cliente (ack por cada frame):
```json
{ "type": "frame_ack", "status": "estable", "payload": { "frame_count": 1, "received": true } }
```

### `/ws/analyze` — progreso del pipeline por etapas
Cliente → servidor:
```json
{ "type": "analyze", "image": "<base64>" }
```
Servidor → cliente (eventos de progreso y resultado final):
```json
{ "type": "progress", "status": "ok",  "payload": { "job_id": "...", "step": "1_captura", "status": 0.1 } }
{ "type": "progress", "status": "ok",  "payload": { "job_id": "...", "step": "2_aruco", "status": 0.4 } }
{ "type": "progress", "status": "ok",  "payload": { "job_id": "...", "step": "2_preprocesamiento", "status": 0.6 } }
{ "type": "progress", "status": "ok",  "payload": { "job_id": "...", "step": "3_filtro", "status": 0.8 } }
{ "type": "result",   "status": "ok",  "payload": { "job_id": "...", "aruco": {...}, "preprocess": {...}, "filter": {...} } }
```

**Etapas de `step`:** `1_captura` → `2_aruco` → `2_preprocesamiento` → `3_filtro`.

---

## 6. Guía rápida para el frontend

1. **Activar cámara:** `POST /api/camera/start` → guarda `session_id`.
2. **Transmitir frames:** abre `/ws/camera` y envía `{type:"frame", image, sensor}`; usa `status` del
   `frame_ack` para avisar al usuario si la captura es estable.
3. **Capturar la mejor toma:** cuando `status === "estable"`, llama `POST /api/capture?session_id=...`.
4. **Analizar:** `POST /api/analyze` (o `/ws/analyze` para mostrar progreso). Lee:
   - `aruco.detected` → si hay marcador para corregir perspectiva.
   - `preprocess.cenital_image` → mostrar la vista corregida.
   - `filter.verdict` y `filter.confidence` → mostrar si hay grieta.

**El `verdict` del filtro depende del modo (`.env` → `APP_MODE`):** en `demo` el filtro
heurístico devuelve `GRIETA/NO_GRIETA` para debugging; en `funcional` requiere el `.tflite`
entrenado. El resto del pipeline (ArUco, escala, parches) funciona igual en ambos modos.

### Integración con la app móvil (`app_grietas/`)

La app Expo/React Native (`App.tsx`) consume **`POST /api/analyze` con JSON base64** (no multipart):

1. El backend debe ejecutarse con `--host 0.0.0.0` para que el celular lo alcance.
2. En `App.tsx` fija `API_URL` a la **IP LAN real** del equipo (ej. `http://192.168.1.27:8000/api/analyze`).
3. Envía `{ "image": "<data-url base64>", "sensor": {...} }` con `Content-Type: application/json`.
4. Renderiza `aruco` (marcador/escala), `preprocess.cenital_image` (vista corregida) y
   `filter.verdict/confidence` (veredicto del filtro).

---

## 7. Roadmap

| Sprint | Trabajo |
| :-- | :-- |
| **1 (este)** | Captura + ArUco + preprocesamiento + contrato de filtro binario (todo funcional). |
| **2** | Entrenar filtro (MobileNetV2 + transfer learning → `.tflite`), inclinación (Canny + Hough). |
| **3** | Segmentación, distancia, fusión multicanal, multiclase (Nivel 1-3), Grad-CAM y mapeo a riesgo. |

---

## 8. Estructura de archivos

```
backend/
  app.py                     # entrypoint FastAPI, CORS, monta routers
  requirements.txt
  core/
    config.py                # rutas, tamaños de parche, umbrales, diccionario ArUco
    schemas.py               # contrato Pydantic (respuestas de la API)
    model_loader.py          # carga del .tflite del filtro (sprint 2: peso)
  services/
    camera.py                # sesión de captura + estabilidad por giróscopo (Sección 1)
    aruco.py                 # detección ArUco, homografía, escala cm/px (Sección 2)
    preprocess.py            # vista cenital + parches 64x64 (Sección 2)
    filter.py                # clasificación binaria por parches (Sección 3)
    training.py              # entrenamiento MobileNetV2 -> .tflite (servicio)
    images.py                # utilidades base64<->imagen
  api/
    router.py                # endpoints REST (/api)
    ws.py                    # endpoints WebSocket (/ws)
  models/                    # filter.tflite (placeholder; peso en sprint 2)
```