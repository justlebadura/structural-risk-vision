# Documentación — Structural Risk Vision

Documentación de onboarding para **cualquier agente de IA** (o desarrollador)
que trabaje en este repositorio: desde los objetivos del proyecto hasta los
documentos técnicos, datos y guías.

> **Cómo usar:** lee este índice para ubicarte. Antes de buscar código a ciegas,
> consulta el índice estructural de **graphify**
> ([`guias/graphify.md`](guias/graphify.md)).

## Índice

### Avance del proyecto
| Documento | Contenido |
|-----------|-----------|
| [`avance_recursos.md`](avance_recursos.md) | Inventario y trazabilidad de recursos (repos, documentos, código, notebooks, datasets, modelos, resultados). |

### Visión (qué y por qué)
| Documento | Contenido |
|-----------|-----------|
| [`vision/objetivos.md`](vision/objetivos.md) | Qué es el proyecto, alcance, entregables y roadmap. |
| [`vision/atractivo_investigativo.md`](vision/atractivo_investigativo.md) | Por qué es interesante a nivel de investigación. |
| [`vision/presentacion.md`](vision/presentacion.md) | Guion de presentación con **CALL TO ACTIONS**. |

### Técnico (cómo está construido)
| Documento | Contenido |
|-----------|-----------|
| [`tecnico/arquitectura.md`](tecnico/arquitectura.md) | Componentes, flujo de datos y contratos entre capas. |
| [`tecnico/estructura.md`](tecnico/estructura.md) | Mapa del repositorio y puntos de entrada por rol. |
| [`tecnico/api_contrato.md`](tecnico/api_contrato.md) | Contrato REST + WebSocket (endpoints y esquemas). |
| [`tecnico/modelos.md`](tecnico/modelos.md) | Modelos binario y segmentador: contrato e integración. |
| [`tecnico/stats_modelo_binario.md`](tecnico/stats_modelo_binario.md) | Métricas del modelo binario (matriz de confusión, F1, recall…). |
| [`tecnico/ejemplo_prediccion.md`](tecnico/ejemplo_prediccion.md) | Predicción de ejemplo del pipeline completo (JSON + imagen anotada). |
| [`tecnico/bitacora_errores.md`](tecnico/bitacora_errores.md) | Errores, imprecisiones, decisiones y pendientes del proceso experimental. |

### Datos
| Documento | Contenido |
|-----------|-----------|
| [`datos/datasets.md`](datos/datasets.md) | Datasets y estructura de `EDA/data/`. |
| [`datos/cifras_clave.md`](datos/cifras_clave.md) | Cifras de titular (generado desde `metricas.json`). |
| [`datos/metricas.json`](datos/metricas.json) | Fuente única de verdad de las métricas del modelo. |
| [`datos/estadisticas.csv`](datos/estadisticas.csv) | Métricas tabuladas (generado). |
| [`datos/ejemplo_prediccion/`](datos/ejemplo_prediccion/) | Entrada, salida JSON e imagen anotada de una predicción concreta. |

### Guías (cómo hacer)
| Documento | Contenido |
|-----------|-----------|
| [`guias/desarrollo.md`](guias/desarrollo.md) | Correr backend/frontend, inferencia real, EDA y convenciones. |
| [`../EDA/README.md`](../EDA/README.md) | Reproducción del EDA con METU y salidas versionadas. |
| [`guias/entrenamiento.md`](guias/entrenamiento.md) | Entrenar/evaluar el modelo binario. |
| [`guias/graphify.md`](guias/graphify.md) | Navegar el código con `graphify-out/graph.json`. |

## Estructura de esta carpeta

```
agents/
├── README.md              # este índice
├── avance_recursos.md     # inventario y trazabilidad de recursos
├── config/settings.json   # configuración de agente (no es documentación)
├── vision/                # objetivos, atractivo, presentación
├── tecnico/               # arquitectura, estructura, API, modelos, stats
├── datos/                 # datasets y estadísticas
└── guias/                 # desarrollo, entrenamiento, graphify
```

## Mapa rápido del repositorio

```
backend/            → API FastAPI (pipeline secciones 1-3) + modelos
frontend/           → App móvil Expo / React Native (cliente)
EDA/                → Cuadernos Jupyter de análisis exploratorio de datos
agents/             → Documentación (este directorio)
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