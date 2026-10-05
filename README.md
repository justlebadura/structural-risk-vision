# Structural Risk Vision — Visión de Riesgo Estructural

**Nombre del proyecto:** Structural Risk Vision
**Descripción:** Sistema de visión por computador para la **detección y evaluación de riesgo estructural** en infraestructura de concreto. A partir de fotografías capturadas con una app móvil detecta **grietas**, estima la **inclinación** de elementos y mapea el resultado a un **nivel de riesgo** (bajo / medio / alto).

Proyecto académico — *Algoritmos y Programación 2026-2 · Ingeniería en Inteligencia Artificial · UIS*.

## Arquitectura

```
┌──────────────┐   REST / WebSocket   ┌──────────────┐   carga   ┌─────────────┐
│   FRONTEND   │ ───────────────────► │   BACKEND    │ ────────► │   MODELOS   │
│  Expo (RN)   │   /api/analyze, /ws  │   FastAPI    │           │  *.tflite   │
└──────────────┘                      └──────────────┘           └─────────────┘
```

- **Backend** — API FastAPI (secciones 1–3 del pipeline) + modelos. Estructura y
  contrato en [`agents/arquitectura.md`](agents/arquitectura.md) y
  [`agents/api_contrato.md`](agents/api_contrato.md).
- **Frontend** — App móvil Expo / React Native (cliente). Código en `frontend/src/`.
- **Modelos** — filtro binario (`model/model_binary`) y segmentador
  (`model/model_segmentator`). Ver [`agents/modelos.md`](agents/modelos.md).
- **EDA** — cuadernos de análisis exploratorio en `EDA/notebooks/`.
- **Documentación para agentes** — objetivos, arquitectura, API, modelos y guías
  en [`agents/README.md`](agents/README.md).

> **Para desarrollar sobre este repo, consulta primero la documentación de
> agentes** (desde objetivos hasta documentos técnicos) en `agents/`, y el
> índice de código `graphify-out/graph.json` (ver [`agents/guias/graphify.md`](agents/guias/graphify.md)).

## Estado del sprint 1

Backend FastAPI con las **secciones 1-3** del pipeline implementadas:

- **Captura** — Marcador ArUco + guía por giróscopo (estabilidad del sensor).
- **Preprocesamiento** — Corrección de perspectiva (homografía) y escala métrica real (cm/píxel).
- **Filtro rápido** — Clasificación binaria grieta/no-grieta por parches (MobileNetV2 → TFLite).

## Puesta en marcha

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuración (`.env` único en la raíz)

La configuración vive en un **único `.env` en la raíz del repositorio** (backend y
frontend lo leen desde ahí; no hay `.env` en subcarpetas). Se crea una copia local
a partir de `.env.example`:

```bash
cp .env.example .env   # ajusta los valores a tu entorno
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `APP_MODE` | `demo` | `demo` → reporte sintético para validar el frontend; `prod` → pipeline real (sin mock). |
| `API_HOST` | `0.0.0.0` | Interfaz de escucha del backend. |
| `API_PORT` | `8000` | Puerto del backend. |
| `LOG_LEVEL` | `info` | Nivel de logging. |
| `EXPO_PUBLIC_API_URL` | — | URL base de la API (la lee el frontend, p. ej. `http://192.168.1.20:8000`). |

- `APP_MODE=demo` (default): `/api/analyze` devuelve un reporte sintético para
  validar el frontend sin marcador ArUco ni modelo entrenado.
- `APP_MODE=prod`: ejecuta el pipeline real (ArUco + preprocesamiento + filtro
  TFLite). Si el `.tflite` aún no existe, el filtro reporta `model_present=false`
  (`verdict="SIN_MODELO"`), nunca datos falsos.

Documentación del contrato de API (para el frontend): http://localhost:8000/docs

## Estructura del repositorio

```
structural-risk-vision/
├── backend/            # API FastAPI + modelos (backend/model/model_binary|model_segmentator)
├── frontend/           # App móvil Expo / React Native (frontend/src/)
├── EDA/                # Cuadernos Jupyter de análisis de datos (EDA/notebooks/)
├── agents/             # Documentación para agentes de IA (objetivos → técnico)
├── graphify-out/       # Índice estructural del código (generado, no versionado)
├── README.md
└── LICENSE
```

## Roadmap

- **Sprint 1 (actual):** captura, ArUco, preprocesamiento y contrato del filtro binario.
- **Sprint 2:** entrenamiento del filtro (transfer learning → `.tflite`), inclinación con OpenCV.
- **Sprint 3:** segmentación, distancia, clasificación multiclase (Nivel 1-3), Grad-CAM y riesgo.

## Licencia

Distribuido bajo la licencia [MIT](LICENSE).