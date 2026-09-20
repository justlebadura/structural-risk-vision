# Structural Risk Vision

Sistema de visión por computador para **detección y evaluación de riesgo estructural**: clasificación de grietas, estimación de inclinación y mapeo a nivel de riesgo (bajo/medio/alto).

Proyecto académico — Algoritmos y Programación 2026-2 · Ingeniería en Inteligencia Artificial · UIS.

## Estado del sprint 1

Backend FastAPI con las **secciones 1-3** del pipeline implementadas:

- **Captura** — Marcador ArUco + guía por giróscopo (estabilidad del sensor).
- **Preprocesamiento** — Corrección de perspectiva (homografía) y escala métrica real (cm/píxel).
- **Filtro rápido** — Clasificación binaria grieta/no-grieta por parches (MobileNetV2 → TFLite).

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Documentación del contrato de API (para el frontend): http://localhost:8000/docs

Detalles técnicos y contrato completo: [`.doc/API Contract y Arquitectura Backend.md`](.doc/API%20Contract%20y%20Arquitectura%20Backend.md)

## Roadmap

- **Sprint 1 (actual):** captura, ArUco, preprocesamiento y contrato del filtro binario.
- **Sprint 2:** entrenamiento del filtro (transfer learning → `.tflite`), inclinación con OpenCV.
- **Sprint 3:** segmentación, distancia, clasificación multiclase (Nivel 1-3), Grad-CAM y riesgo.