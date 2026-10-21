# Objetivos del Proyecto

## Qué es

**Structural Risk Vision** es un sistema de visión por computador para la
**detección y evaluación de riesgo estructural** en infraestructura de concreto.
A partir de fotografías (tomadas desde una app móvil) detecta **grietas**,
estima la **inclinación** de elementos y mapea el resultado a un **nivel de
riesgo** (bajo / medio / alto).

Es un **proyecto académico** — *Algoritmos y Programación 2026-2 · Ingeniería en
Inteligencia Artificial · UIS*.

## Objetivo general

Construir un pipeline completo de inspección estructural asistida por IA que
vaya de la **captura de imagen** a un **veredicto de riesgo**, integrando:

1. **Captura** guiada (marcador ArUco + estabilidad por giróscopo).
2. **Preprocesamiento** (corrección de perspectiva y escala métrica real).
3. **Filtro rápido** (clasificación binaria grieta/no-grieta por parches).
4. **Inclinación aparente del elemento** (Canny + Hough sobre la imagen).
5. **Segmentación** y **medición** (grosor, transformada de distancia).
6. **Severidad / riesgo** (clasificación multiclase: Nivel 1–3).

## Alcance (deliverables por componente)

| Componente | Entrega |
|-----------|---------|
| **Backend** | API FastAPI REST + WebSocket con el pipeline secciones 1–3 implementado, contrato de API en `/docs`, modo demo controlado por entorno. |
| **Frontend** | App móvil Expo/React Native que captura, envía al backend y muestra el reporte. |
| **Modelos** | Filtro binario (`model_binary`) y segmentador (`model_segmentator`), con contrato de integración definido. |
| **EDA** | Cuaderno de clasificación ejecutado sobre METU real con salidas versionadas y cuaderno de segmentación en modo simulación etiquetado. |

## Roadmap por sprint

- **Sprint 1 (hecho):** captura, ArUco, preprocesamiento y contrato del filtro
  binario. Backend funcional en `APP_MODE=demo` para validar el frontend.
- **Sprint 2 (hecho):** filtro binario entrenado (`filter.tflite`), inclinación
  del elemento con Canny + Hough y app lista para inferencia real
  (`APP_MODE=prod`).
- **Sprint 3 (en desarrollo):** segmentación semántica, transformada de
  distancia, clasificación multiclase (Nivel 1–3), Grad-CAM y nivel de riesgo.

> La inclinación implementada es **aparente respecto al eje de la imagen**; no
> sustituye una medición absoluta con inclinómetro. La validación se hizo con
> METU y una escena sintética reproducible, no con fotos propias de campo.

## Principios no negociables

- **Honestidad de datos:** el EDA distingue claramente el *dataset real* del
  *modo simulación*; nunca se presentan resultados sintéticos como hallazgos reales.
- **Sin mocks silenciosos:** el backend reporta con claridad cuándo un modelo no
  está disponible (`SIN_MODELO`), en lugar de inventar resultados.
- **Configuración por entorno:** el modo de ejecución y los parámetros viven en
  `.env` (ver [`guias/desarrollo.md`](../guias/desarrollo.md)).