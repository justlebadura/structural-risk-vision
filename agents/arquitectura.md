# Arquitectura del Sistema

Vista general de componentes, estructura de carpetas y flujo de datos entre las
capas **Frontend → Backend → Modelos**.

## Componentes y flujo

```
┌────────────────────────┐      REST / WebSocket      ┌──────────────────────────────┐
│      FRONTEND          │  ───────────────────────►  │          BACKEND             │
│  App móvil Expo (RN)   │   POST /api/analyze        │         FastAPI              │
│  frontend/src/         │   + WS /ws/analyze         │         backend/             │
└────────────────────────┘                            │  ├─ api/    (router, ws)     │
                                                      │  ├─ core/   (config, schemas,│
                                                      │  │           model_loader)    │
                                                      │  ├─ services/(aruco, camera, │
                                                      │  │           preprocess,      │
                                                      │  │           filter, images,  │
                                                      │  │           demo)            │
                                                      │  └─ model/  (model_binary,   │
                                                      │              model_segmentator)│
                                                      └───────────────┬──────────────┘
                                                                     │ carga
                                                             ┌───────▼────────┐
                                                             │    MODELOS      │
                                                             │  *.tflite        │
                                                             └────────────────┘
```

## Estructura de carpetas

```
structural-risk-vision/
├── backend/                    # API FastAPI + modelos
│   ├── app.py                  # entrypoint: monta routers REST + WS, CORS
│   ├── api/
│   │   ├── router.py           # endpoints REST (/api/*)
│   │   └── ws.py               # endpoints WebSocket (/ws/*)
│   ├── core/
│   │   ├── config.py           # configuración central (+ carga de .env)
│   │   ├── schemas.py          # contratos Pydantic de la API
│   │   └── model_loader.py     # puente hacia los modelos (singleton)
│   ├── services/
│   │   ├── aruco.py            # sección 2: detección ArUco + homografía
│   │   ├── camera.py           # sección 1: sesión de cámara / estabilidad
│   │   ├── preprocess.py       # sección 2: vista cenital, parches 64x64
│   │   ├── filter.py           # sección 3: clasificación binaria por parches
│   │   ├── images.py           # codificar/decodificar base64
│   │   └── demo.py             # modo demo: reporte sintético
│   ├── model/
│   │   ├── model_binary/       # filtro binario (binary_model.py + README)
│   │   └── model_segmentator/  # segmentador (placeholder, sprint 3)
│   └── requirements.txt
├── frontend/                   # App móvil Expo / React Native
│   ├── App.tsx                 # entrypoint mínimo
│   └── src/
│       ├── api/inspect.ts      # cliente HTTP hacia /api/analyze
│       ├── components/         # PermissionView, CameraOverlay, ShutterButton, ResultModal
│       ├── constants/layout.ts
│       ├── screens/CameraScreen.tsx
│       ├── theme/colors.ts
│       └── types/inspection.ts # tipos del reporte
├── EDA/
│   └── notebooks/              # análisis exploratorio (01 clasificación, 02 segmentación)
├── agents/                     # documentación para agentes (este directorio)
└── graphify-out/               # índice estructural del código (generado)
```

## Pipeline de datos (secciones 1–3)

1. **Captura** — El frontend captura un frame (base64) + datos del giróscopo.
2. **ArUco** — `services/aruco.py` detecta el marcador y calcula la homografía
   y la escala `cm/píxel`.
3. **Preprocesamiento** — `services/preprocess.py` corrige la perspectiva
   (vista cenital) y divide en parches `64×64`.
4. **Filtro rápido** — `services/filter.py` usa el `model_binary` para
   clasificar cada parche y devolver el veredicto.
5. **Respuesta** — `AnalyzeResponse` con `aruco`, `preprocess` y `filter`.

## Modos de ejecución

Controlado por `APP_MODE` en el `.env` de la raíz (ver `core/config.py`):

- **`demo`** (default): `/api/analyze` responde un reporte sintético
  (`services/demo.py`) para validar el frontend sin hardware ni modelo.
- **`prod`**: ejecuta el pipeline real. Sin modelo entrenado, el filtro
  responde `model_present=false` y `verdict="SIN_MODELO"` (nunca un mock).

## Contratos entre capas

- **Backend → Frontend:** esquemas Pydantic en `core/schemas.py` (contrato único,
  expuesto en `/docs`). El frontend solo consume estos modelos.
- **Backend → Modelos:** el modelo binario se carga vía
  `core/model_loader.get_filter_model()`. Su contrato está documentado en
  [`modelos.md`](modelos.md) y en `backend/model/model_binary/README.md`.
- **Catálogo de endpoints:** ver [`api_contrato.md`](api_contrato.md).