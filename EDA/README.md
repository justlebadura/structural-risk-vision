# Análisis Exploratorio de Datos (EDA)

Cuadernos de exploración y análisis previo para las distintas etapas del pipeline de
**detección de grietas e inclinación estructural**.

## Cuadernos

| #  | Cuaderno | Foco |
|----|----------|------|
| 01 | [`notebooks/01_clasificacion_grietas.ipynb`](notebooks/01_clasificacion_grietas.ipynb) | Análisis de integridad, univariado/bivariado e hipótesis para la clasificación binaria de grietas. |
| 02 | [`notebooks/02_pipeline_segmentacion_severidad.ipynb`](notebooks/02_pipeline_segmentacion_severidad.ipynb) | Pipeline avanzado: segmentación, transformada de distancia, factor de escala ArUco y severidad. |

## Comportamiento de los cuadernos

Cada cuaderno intenta **cargar el dataset real** desde `EDA/data/`. Si los datos no están presentes,
entra en **modo simulación** (genera datos sintéticos) y **lo etiqueta explícitamente en pantalla**:
los resultados de la simulación solo demuestran la metodología y **no** deben presentarse como
hallazgos sobre el dataset real.

### Estructura esperada en `EDA/data/`

**Cuaderno 01 (clasificación)** — METU o SDNET2018:

```
data/metu/Positive/*.jpg
data/metu/Negative/*.jpg
# o bien SDNET2018:
data/sdnet2018/{C,D,M}/{train,test}/{crack,uncracked}/*.png
```

**Cuaderno 02 (segmentación)** — Crack500 o CFD:

```
data/crack500/images/*.jpg   data/crack500/masks/*.png
data/cfd/*.jpg               data/cfd/*_mask.png
```

> Si los datos viven en otra ruta, anúlala con la variable de entorno `EDA_DATA_DIR`.

## Notas metodológicas

- **Sin tautología (cuaderno 02, hipótesis 2):** la severidad se asigna como etiqueta de referencia
  **independiente** (con ruido) y se testea su asociación con el grosor **medido** de la máscara.
  La severidad *no* se deriva del grosor medido, por lo que la correlación no es auto-cumplida.
- **Bins LBP corregidos:** un LBP uniforme con `P=8` tiene exactamente `P+2 = 10` patrones.

## Datos

Los datasets (`Concrete Crack Images`, `SDNET2018`, `Crack500`, `CFD`) **no se versionan** en el
repositorio por tamaño y licencia; se colocan localmente bajo `EDA/data/` (ignorado por `.gitignore`).