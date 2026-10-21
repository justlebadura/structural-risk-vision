# Avance del Proyecto — Recursos

El avance del proyecto comprende la **organización, desarrollo y documentación**
de los diferentes recursos técnicos y académicos generados durante su ejecución.
En este apartado se relacionan los repositorios de código fuente, documentos
técnicos, informes, scripts, notebooks, modelos implementados, conjuntos de datos
utilizados o generados, resultados experimentales y demás archivos asociados al
proyecto.

Para cada recurso se procura incluir su **ubicación o enlace de acceso**, una
**breve descripción** de su contenido, su **propósito** dentro del proyecto y,
cuando corresponda, la **versión o estado actual** de desarrollo. Esta
organización permite mantener la trazabilidad de las actividades realizadas,
facilitar la reproducción de los experimentos y centralizar la información
necesaria para el seguimiento y continuidad del proyecto.

Entre los elementos registrados se pueden incluir repositorios en GitHub o
plataformas institucionales, documentos de formulación y seguimiento, códigos de
preprocesamiento, entrenamiento y evaluación, datasets originales y procesados,
modelos entrenados, configuraciones experimentales, figuras, resultados y
documentación de soporte. Los recursos se actualizarán progresivamente de acuerdo
con los avances alcanzados en cada etapa del proyecto.

> **Estado de referencia:** rama `development` · consultar el último commit con `git log -1`.

---

## 1. Repositorios

| Recurso | Ubicación | Descripción | Propósito | Estado / versión |
|---------|-----------|-------------|-----------|------------------|
| Repo principal | `https://github.com/justlebadura/structural-risk-vision` (rama `development`) | Backend FastAPI, app móvil Expo, cuadernos EDA, modelos y documentación. | Núcleo del proyecto y colaboración. | Activo, sprint 2 |
| Repo de presentación | `structural-risk-vision-slides/` (repositorio aparte) | Diapositivas web (HTML/CSS/JS) con motion graphics. | Difusión y presentación del proyecto. | v1, estático |

## 2. Documentación de formulación y seguimiento

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| Objetivos | [`vision/objetivos.md`](vision/objetivos.md) | Alcance, entregables y roadmap por sprint. | Formulación y seguimiento. | Vigente |
| Atractivo investigativo | [`vision/atractivo_investigativo.md`](vision/atractivo_investigativo.md) | Aportes técnicos y preguntas de investigación. | Sustento académico. | Vigente |
| Presentación | [`vision/presentacion.md`](vision/presentacion.md) | Guion de diapositivas y call-to-actions. | Difusión. | Vigente |
| Recursos (este documento) | [`avance_recursos.md`](avance_recursos.md) | Inventario y trazabilidad de recursos. | Centralizar información. | Vigente |

## 3. Documentación técnica y guías

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| Arquitectura | [`tecnico/arquitectura.md`](tecnico/arquitectura.md) | Componentes, flujo de datos y contratos entre capas. | Referencia técnica. | Vigente |
| Estructura | [`tecnico/estructura.md`](tecnico/estructura.md) | Mapa del repositorio y puntos de entrada. | Onboarding. | Vigente |
| Contrato de API | [`tecnico/api_contrato.md`](tecnico/api_contrato.md) | Endpoints REST + WebSocket y esquemas. | Integración frontend. | Vigente |
| Modelos | [`tecnico/modelos.md`](tecnico/modelos.md) | Modelo binario y segmentador; integración. | Referencia de modelos. | Vigente |
| Métricas del modelo | [`tecnico/stats_modelo_binario.md`](tecnico/stats_modelo_binario.md) | Confusión, F1, recall, AUC, época y ajuste. | Validación experimental. | Generado |
| Bitácora de errores | [`tecnico/bitacora_errores.md`](tecnico/bitacora_errores.md) | Errores, imprecisiones, decisiones y pendientes. | Trazabilidad del proceso. | Vigente |
| Guía de desarrollo | [`guias/desarrollo.md`](guias/desarrollo.md) | Ejecución, `.env`, convenciones. | Reproducibilidad. | Vigente |
| Guía de entrenamiento | [`guias/entrenamiento.md`](guias/entrenamiento.md) | Entrenar/evaluar el modelo binario. | Reproducir experimentos. | Vigente |
| Guía graphify | [`guias/graphify.md`](guias/graphify.md) | Navegación del código por índice estructural. | Navegación. | Vigente |

## 4. Código fuente y scripts

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| API REST | `backend/api/router.py` | 9 endpoints `/api/*` del pipeline, incluyendo inclinación. | Servicio al frontend. | Sprint 1–3 |
| WebSocket | `backend/api/ws.py` | `/ws/camera` y `/ws/analyze`. | Streaming/progreso. | Sprint 1 |
| Configuración | `backend/core/config.py` | Constantes y carga del `.env` raíz. | Configuración central. | Vigente |
| Esquemas | `backend/core/schemas.py` | Contratos Pydantic de la API. | Único contrato. | Vigente |
| Carga de modelos | `backend/core/model_loader.py` | Singleton del modelo binario. | Integración backend↔modelo. | Vigente |
| Captura/superficie | `backend/services/camera.py` | Estabilidad (giróscopo) y superficie (acelerómetro). | Sección 1. | Vigente |
| ArUco/normalización | `backend/services/aruco.py` | Ángulo, homografía y escala (vista cenital). | Sección 2. | Vigente |
| Inclinación del elemento | `backend/services/inclination.py` | Canny + Hough, referencia vertical/horizontal y confianza. | Sección 2b. | Vigente |
| Verificación de inferencia | `backend/scripts/verificar_inferencia.py` | Comprueba modelo TFLite y ejecuta una predicción. | Preparar app/backend. | Generado |
| Predicción de ejemplo | `backend/scripts/prediccion_ejemplo.py` | Escena METU + ArUco, JSON e imagen anotada. | Evidencia end-to-end. | Generado |
| Preprocesamiento | `backend/services/preprocess.py` | Vista cenital y parches 64×64. | Sección 2. | Vigente |
| Filtro binario | `backend/services/filter.py` | Clasificación por parches. | Sección 3. | Vigente |
| Modo demo | `backend/services/demo.py` | Reporte sintético. | Validar frontend sin hardware. | Vigente |
| **Preprocesamiento (IA)** | `backend/model/model_binary/data.py` | Carga METU y augmentación. | Datos de entrenamiento. | Sprint 2 |
| **Modelo (IA)** | `backend/model/model_binary/model.py` | U-Net ligera y MobileNetV2. | Arquitecturas. | Sprint 2 |
| **Entrenamiento (IA)** | `backend/model/model_binary/train.py` | Entrena y exporta TFLite. | Reproducir entrenamiento. | Sprint 2 |
| **Evaluación (IA)** | `backend/model/model_binary/evaluate.py` | Métricas y reporte. | Validación. | Sprint 2 |
| Inferencia TFLite | `backend/model/model_binary/binary_model.py` | Carga `filter.tflite`. | Runtime del backend. | Sprint 2 |
| Frontend | `frontend/src/**` | Pantallas, componentes, cliente API y verificación de `/api/health`. | App móvil e inferencia real. | Vigente |

## 5. Notebooks y análisis (EDA)

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| EDA clasificación | `EDA/notebooks/01_clasificacion_grietas.ipynb` | Integridad, univariado/bivariado, hipótesis y robustez ante sombras sobre METU real. | Insumos del modelo binario. | Ejecutado con salidas (muestra 2k/clase) |
| EDA segmentación | `EDA/notebooks/02_pipeline_segmentacion_severidad.ipynb` | Segmentación, distancia y severidad. | Insumos del sprint 3. | Ejecutado en simulación |
| Reproducción EDA | `EDA/README.md` · `EDA/requirements.txt` | Comandos, dependencias y alcance de la muestra. | Reproducibilidad. | Vigente |

## 6. Conjuntos de datos

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| METU (Concrete Crack Images) | `EDA/data/metu/{train,validation,test}/{Positive,Negative}` | 40 000 imágenes 227×227 (20 000/20 000); splits 24k/8k/8k. Fuente: Özgenel (2019), doi:10.17632/5y9wdsg2zt.2. | Entrenar/validar el modelo binario. | Local (no versionado) |
| SDNET2018 / Crack500 / CFD | `EDA/data/…` | Alternativas de clasificación y segmentación. | Soporte a EDA y sprint 3. | Opcional |

> Los datasets no se versionan (tamaño/licencia); se descargan localmente. Ver
> [`datos/datasets.md`](datos/datasets.md).

## 7. Modelos entrenados y artefactos

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| U-Net ligera (desplegada) | `backend/model/model_binary/filter.tflite` | 121 883 params · 492 KB · TFLite. | Filtro binario del backend. | Generado (no versionado) |
| U-Net (checkpoint) | `backend/model/model_binary/artifacts/unet.keras` | Pesos Keras + historial. | Reentrenar/evaluar. | Generado |
| MobileNetV2 (baseline) | `backend/model/model_binary/artifacts/mobilenetv2.keras` | Transfer learning ImageNet. | Comparación. | Generado |
| Segmentador | `backend/model/model_segmentator/` | Reservado. | Sprint 3. | Pendiente |

## 8. Configuración experimental

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| Plantilla de entorno | `.env.example` | `APP_MODE`, `API_PORT`, `EXPO_PUBLIC_API_URL`, etc. | Configuración reproducible. | Vigente |
| Dependencias backend | `backend/requirements.txt` | Runtime FastAPI/OpenCV/TFLite. | Reproducir el servicio. | Vigente |
| Dependencias entrenamiento | `backend/model/model_binary/requirements-train.txt` | TensorFlow, scikit-learn, matplotlib. | Reproducir el modelo. | Vigente |
| Hiperparámetros | `backend/model/model_binary/train.py` (args) | Épocas, batch, LR, augmentación, early stopping. | Trazabilidad experimental. | Sprint 2 |

## 9. Resultados experimentales y figuras

| Recurso | Ubicación | Descripción | Propósito | Estado |
|---------|-----------|-------------|-----------|--------|
| Fuente de verdad | [`datos/metricas.json`](datos/metricas.json) | Métricas crudas + diagnóstico de ajuste. | Base de todo lo demás. | Generado |
| Métricas tabuladas | [`datos/estadisticas.csv`](datos/estadisticas.csv) | Métricas por modelo y su significado. | Análisis/seguimiento. | Generado |
| Cifras clave | [`datos/cifras_clave.md`](datos/cifras_clave.md) | Titulares (F1, recall, AUC, tamaño, latencia). | Presentaciones. | Generado |
| Matrices de confusión | `agents/tecnico/confusion_{unet,mobilenetv2}.png` | TP/TN/FP/FN por modelo. | Evidencia visual. | Generado |
| Curvas de entrenamiento | `agents/tecnico/training_{unet,mobilenetv2}.png` | Loss y AUC train/val por época. | Diagnosticar over/underfitting. | Generado |
| Predicción de ejemplo | `agents/datos/ejemplo_prediccion/` | Entrada, salida JSON e imagen anotada. | Evidencia end-to-end. | Generado |
| Reporte de ejemplo | `agents/tecnico/ejemplo_prediccion.md` | Lectura y reproducción del ejemplo. | Documentación. | Vigente |
| Índice de código | `graphify-out/graph.json` | Grafo estructural del código. | Navegación. | Generado |

## 10. Convenciones de versionado

- **Se versionan:** código, documentación (`agents/`), notebooks ejecutados,
  configuraciones de ejemplo (`.env.example`, `requirements*.txt`) y resultados
  tabulados (`agents/datos/*`).
- **No se versionan** (`.gitignore`): `*.tflite`, `artifacts/` (checkpoints
  `.keras` e historiales), `EDA/data/` (datasets) y `graphify-out/`. Se regeneran
  localmente con los scripts correspondientes.
- **Entorno:** los secretos y la configuración viven en el `.env` de la raíz
  (ignorado); solo se versiona la plantilla `.env.example`.
