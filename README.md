# Structural Risk Vision

Sistema de visión por computador para **detección y evaluación de riesgo estructural**: clasificación de grietas, estimación de inclinación y mapeo a nivel de riesgo (bajo/medio/alto).

Proyecto académico — Algoritmos y Programación 2026-2 · Ingeniería en Inteligencia Artificial · UIS.

## Estado del sprint 1

Backend FastAPI con las **secciones 1-3** del pipeline implementadas:

- **Captura** — Marcador ArUco + guía por giróscopo (estabilidad del sensor).
- **Preprocesamiento** — Corrección de perspectiva (homografía) y escala métrica real (cm/píxel).
- **Filtro rápido** — Clasificación binaria grieta/no-grieta por parches (MobileNetV2 → TFLite).
- **Entrenamiento** — Endpoints de entrenamiento, estado y subida del modelo.

### Modo de ejecución (`APP_MODE` en `.env`)

El backend funciona en dos modos controlados desde `.env` en la raíz:

| Modo | Comportamiento del filtro |
| :-- | :-- |
| `demo` (por defecto) | Usa un filtro **heurístico** (sin modelo) para debugging del pipeline y la UI. No requiere modelo. |
| `funcional` | Usa el modelo real `backend/models/filter.tflite` (inferencia real). |

En `funcional` sin `.tflite` desplegado, el backend lo reporta con claridad
(`backend: "none"`) en vez de fallar. Copia `.env.example` a `.env` para ajustarlo.

## Backend

```bash
cd backend
pip install -r requirements.txt
# Para que un celular en la misma red local alcance la API, exponer en 0.0.0.0
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Documentación del contrato de API (para el frontend): http://localhost:8000/docs

Detalles técnicos y contrato completo: [`.doc/API Contract y Arquitectura Backend.md`](.doc/API%20Contract%20y%20Arquitectura%20Backend.md)

## Roadmap

- **Sprint 1 (actual):** captura, ArUco, preprocesamiento, contrato del filtro binario y endpoints de entrenamiento.
- **Sprint 2:** entrenar el filtro (transfer learning → `.tflite`), inclinación con OpenCV.
- **Sprint 3:** segmentación, distancia, clasificación multiclase (Nivel 1-3), Grad-CAM y riesgo.