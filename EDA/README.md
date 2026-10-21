# EDA — Análisis Exploratorio de Datos

Cuadernos de análisis del proyecto y su forma de reproducción.

## Cuadernos

| Cuaderno | Estado | Datos |
|----------|--------|-------|
| [`01_clasificacion_grietas.ipynb`](notebooks/01_clasificacion_grietas.ipynb) | Ejecutado y versionado con salidas | METU real, muestra estratificada |
| [`02_pipeline_segmentacion_severidad.ipynb`](notebooks/02_pipeline_segmentacion_severidad.ipynb) | Ejecutado con salidas de **simulación** | Faltan máscaras Crack500/CFD |

El cuaderno 01 se ejecutó con **4,000 imágenes reales de METU** (2,000 por
clase) usando una muestra reproducible (`seed=42`). No es el dataset completo;
para reproducir el dataset entero usa `EDA_SAMPLE_PER_CLASS=0` en una máquina
con RAM suficiente.

El cuaderno 02 conserva sus salidas de **modo simulación** porque el repositorio
no incluye máscaras reales de segmentación. Esas salidas demuestran la
metodología, no hallazgos sobre Crack500/CFD.

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r EDA/requirements.txt
```

## Datos

Los datasets no se versionan (tamaño/licencia). Estructura esperada:

```text
EDA/data/
└── metu/
    ├── train/{Positive,Negative}/*.jpg
    ├── validation/{Positive,Negative}/*.jpg
    └── test/{Positive,Negative}/*.jpg
```

Para segmentación:

```text
EDA/data/crack500/images/*.jpg
EDA/data/crack500/masks/*.png
EDA/data/cfd/*.jpg
EDA/data/cfd/*_mask.png
```

Más detalles en [`../agents/datos/datasets.md`](../agents/datos/datasets.md).

## Reproducir el cuaderno 01

Desde la raíz del repositorio:

```bash
EDA_DATA_DIR=EDA/data EDA_SAMPLE_PER_CLASS=2000 \
python -m nbconvert --to notebook --execute --inplace \
  EDA/notebooks/01_clasificacion_grietas.ipynb
```

- `EDA_DATA_DIR`: ruta al directorio de datos.
- `EDA_SAMPLE_PER_CLASS`: imágenes por clase (`0` = dataset completo).

El cuaderno detecta automáticamente si hay datos reales; si no, entra en modo
simulación y lo etiqueta en pantalla.
