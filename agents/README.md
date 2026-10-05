# Guía para Agentes de IA — Structural Risk Vision

Documentación de onboarding para **cualquier agente de IA** (o desarrollador)
que trabaje en este repositorio: desde los objetivos del proyecto hasta los
documentos técnicos de la API, los modelos y las guías de desarrollo.

> **Cómo usar:** lee este índice para ubicarte. Antes de buscar código a ciegas,
> consulta el índice estructural generado por **graphify** (ver
> [`guias/graphify.md`](guias/graphify.md)); te dice qué símbolos hay y en qué
> archivo viven sin adivinar nombres.

## Índice de documentos

| Documento | Contenido |
|-----------|-----------|
| [`objetivos.md`](objetivos.md) | Qué es el proyecto, alcance, entregables y roadmap por sprint. |
| [`arquitectura.md`](arquitectura.md) | Componentes, estructura de carpetas, flujo de datos y contratos entre capas. |
| [`api_contrato.md`](api_contrato.md) | Contrato REST + WebSocket: endpoints, esquemas y ejemplos de request/response. |
| [`modelos.md`](modelos.md) | Modelos binario y segmentador: dónde viven, qué contrato deben cumplir y cómo se integran. |
| [`guias/desarrollo.md`](guias/desarrollo.md) | Cómo correr backend/frontend, configuración de entorno (`.env`), convenciones. |
| [`guias/graphify.md`](guias/graphify.md) | Cómo navegar el código con el índice `graphify-out/graph.json`. |

## Mapa rápido del repositorio

```
backend/            → API FastAPI (pipeline secciones 1-3) + modelos
frontend/           → App móvil Expo / React Native (cliente)
EDA/                → Cuadernos Jupyter de análisis exploratorio de datos
agents/             → Documentación para agentes (este directorio)
graphify-out/       → Índice estructural del código (generado, no versionado)
```

## Reglas transversales

- **Nunca mockear en producción.** En `APP_MODE=prod`, si el modelo no existe,
  el backend responde `model_present=false` / `SIN_MODELO`; no datos falsos.
- **Los secretos y el entorno van en `.env`** (ignorados por git). Solo se
  versionan los `.env.example`.
- **Los binarios pesados no se versionan**: modelos `*.tflite` y datasets en
  `EDA/data/` están en `.gitignore`.
- **Idioma del código/documentación:** español (consistente con el proyecto).
- Antes de tocar código, **consulta graphify** para ubicar los símbolos.