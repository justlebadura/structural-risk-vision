# Estructura del Proyecto

Mapa completo del repositorio, componente por componente.

```
structural-risk-vision/
│
├── backend/                         # API FastAPI (pipeline secciones 1–3)
│   ├── app.py                       # entrypoint: monta REST + WS, CORS
│   ├── api/
│   │   ├── router.py                # 9 endpoints REST (/api/*)
│   │   └── ws.py                    # 2 WebSockets (/ws/camera, /ws/analyze)
│   ├── core/
│   │   ├── config.py                # configuración central + carga del .env raíz
│   │   ├── schemas.py               # contratos Pydantic (única fuente de verdad)
│   │   └── model_loader.py          # singleton del modelo binario
│   ├── services/
│   │   ├── aruco.py                 # sección 2: ArUco + ángulo + homografía (cenital)
│   │   ├── camera.py                # sección 1: estabilidad (giróscopo) + superficie (acelerómetro)
│   │   ├── inclination.py           # sección 2b: inclinación Canny + Hough
│   │   ├── preprocess.py            # sección 2: vista cenital + parches 64×64
│   │   ├── filter.py                # sección 3: clasificación binaria por parches
│   │   ├── images.py                # (de)codificación base64
│   │   └── demo.py                  # modo demo: reporte sintético
│   ├── model/
│   │   ├── model_binary/            # ★ filtro binario (sección 3)
│   │   │   ├── binary_model.py      #   carga TFLite + contrato de inferencia
│   │   │   ├── data.py              #   carga METU + augmentación
│   │   │   ├── model.py             #   U-Net ligera + MobileNetV2
│   │   │   ├── train.py             #   entrenamiento + export TFLite
│   │   │   └── evaluate.py          #   métricas + reporte de stats
│   │   └── model_segmentator/       # segmentador semántico (sprint 3, placeholder)
│   ├── scripts/
│   │   ├── verificar_inferencia.py # comprueba modelo TFLite + predicción
│   │   └── prediccion_ejemplo.py   # escena + JSON + imagen anotada
│   └── requirements.txt             # runtime del backend
│
├── frontend/                        # App móvil Expo / React Native
│   ├── App.tsx                      # navegación mínima: menú → ubicación → cámara
│   ├── metro.config.js              # lee el .env de la raíz
│   └── src/
│       ├── api/inspect.ts           # cliente HTTP → /api/analyze + /api/health
│       ├── components/              # PermissionView, CameraOverlay, ShutterButton, ResultModal
│       ├── constants/               # layout.ts, inspection.ts (elementos estructurales)
│       ├── screens/                 # MenuScreen, LocationScreen, CameraScreen
│       ├── types/inspection.ts      # tipos del reporte
│       ├── theme/                   # colores
│       └── assets/                  # iconos/splash
│
├── EDA/                             # Análisis Exploratorio de Datos
│   ├── notebooks/
│   │   ├── 01_clasificacion_grietas.ipynb          # EDA real con salidas (METU)
│   │   └── 02_pipeline_segmentacion_severidad.ipynb # segmentación (simulación)
│   ├── data/                        # datasets (METU), NO versionado
│   ├── README.md                    # reproducción del EDA
│   └── requirements.txt             # dependencias del EDA
│
├── agents/                          # ★ documentación
│   ├── README.md                    # índice de navegación
│   ├── config/settings.json         # configuración de agente (no es doc)
│   ├── vision/                      # objetivos, atractivo, presentación
│   ├── tecnico/                     # arquitectura, estructura, API, modelos, stats
│   ├── datos/                       # datasets, estadísticas y ejemplo_prediccion/
│   └── guias/                       # desarrollo, entrenamiento, graphify
│
├── graphify-out/                    # índice estructural del código (generado)
├── .env.example                     # plantilla de configuración (raíz)
├── README.md
└── LICENSE
```

## Flujo de datos end-to-end

```
Menú → Ubicación (elemento + texto)
   │
   ▼
Cámara móvil
   │  frame base64 + giróscopo (estabilidad) + acelerómetro (superficie) + contexto
   ▼
[Frontend Expo]  ── POST /api/analyze ──►  [Backend FastAPI]
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
                 Sección 1: Captura    Sección 2: ArUco+pre    Sección 3: Filtro
                 (estabilidad +        (ángulo → homografía,   (model_binary:
                  superficie)           escala, parches 64×64)  U-Net → P(grieta))
                        │                     │
                        └── Sección 2b: inclinación Canny+Hough
                        └─────────────────────┼─────────────────────┘
                                              ▼
                                    AnalyzeResponse (JSON)
                                    (mode · demo · aruco · preprocess · filter ·
                                     inclination · surface · element · location)
                                              │
   ◄──────────────────────────────────────────┘
   [Frontend] muestra reporte: veredicto + vista cenital + ubicación + confianza
```

## Puntos de entrada por rol

| Quiero… | Empieza por |
|---------|-------------|
| Entender el proyecto | [`objetivos.md`](../vision/objetivos.md) |
| Ver la arquitectura | [`arquitectura.md`](arquitectura.md) |
| Consumir la API | [`api_contrato.md`](api_contrato.md) |
| Trabajar en el modelo | [`modelos.md`](modelos.md) + `backend/model/model_binary/` |
| Correr el proyecto | [`guias/desarrollo.md`](../guias/desarrollo.md) |
| Navegar el código | [`guias/graphify.md`](../guias/graphify.md) |
| Hacer una presentación | [`presentacion.md`](../vision/presentacion.md) + [`estadisticas.csv`](../datos/estadisticas.csv) |