# Datasets y EDA

Datasets usados por el proyecto y los cuadernos de **Análisis Exploratorio de
Datos** (`EDA/notebooks/`).

## Cuadernos

| #  | Cuaderno | Foco |
|----|----------|------|
| 01 | [`01_clasificacion_grietas.ipynb`](../../EDA/notebooks/01_clasificacion_grietas.ipynb) | Integridad, univariado/bivariado e hipótesis. **Ejecutado con METU real y salidas versionadas** (muestra 2,000/clase). |
| 02 | [`02_pipeline_segmentacion_severidad.ipynb`](../../EDA/notebooks/02_pipeline_segmentacion_severidad.ipynb) | Segmentación, transformada de distancia, escala ArUco y severidad. Salidas de **simulación** (faltan máscaras Crack500/CFD). |

Cada cuaderno intenta **cargar el dataset real** desde `EDA/data/`. Si no está
presente, entra en **modo simulación** (datos sintéticos) y **lo etiqueta en
pantalla**: los resultados de la simulación solo demuestran la metodología y
**no** deben presentarse como hallazgos sobre el dataset real.

El cuaderno 01 se versionó con salidas reales usando `EDA_SAMPLE_PER_CLASS=2000`
(4,000 imágenes, semilla 42). Para el dataset completo:

```bash
EDA_DATA_DIR=EDA/data EDA_SAMPLE_PER_CLASS=0 \
python -m nbconvert --to notebook --execute --inplace \
  EDA/notebooks/01_clasificacion_grietas.ipynb
```

Ver [`EDA/README.md`](../../EDA/README.md) para requisitos y reproducibilidad.

## Datasets

| Dataset | Uso | Estructura esperada en `EDA/data/` |
|---------|-----|-------------------------------------|
| **METU** (Concrete Crack Images, Özgenel) | Clasificación binaria + entrenamiento del modelo | `metu/{train,validation,test}/{Positive,Negative}/*.jpg` |
| **SDNET2018** | Clasificación binaria (alternativa) | `sdnet2018/{C,D,M}/{train,test}/{crack,uncracked}/*.png` |
| **Crack500 / CFD** | Segmentación / severidad | `crack500/{images,masks}/*` · `cfd/*` + `*_mask.png` |

- **METU**: 40,000 imágenes `227×227` (20,000 grieta / 20,000 sin grieta), splits
  oficiales 24k/8k/8k. Fuente: Özgenel, Ç.F. (2019), *Concrete Crack Images for
  Classification*, Mendeley Data, doi:10.17632/5y9wdsg2zt.2.
- Rutas alternas: `EDA_DATA_DIR` (cuadernos) y `METU_DATA_DIR` (entrenamiento).

> Los datasets **no se versionan** (tamaño/licencia); se colocan localmente bajo
> `EDA/data/` (ignorado por `.gitignore`).

## Notas metodológicas

- **Sin tautología (cuaderno 02, hipótesis 2):** la severidad se asigna como
  etiqueta de referencia **independiente** (con ruido) y se testea su asociación
  con el grosor **medido**. No se deriva del grosor, así la correlación no es
  auto-cumplida.
- **Bins LBP corregidos:** un LBP uniforme con `P=8` tiene exactamente
  `P+2 = 10` patrones.
- **Robustez ante sombras:** el cuaderno 01 mide el efecto de sombras suaves y
  duras. Una sombra dura dispara el FPR porque su borde recto se parece a una
  grieta. Decisiones y cifras en
  [`../tecnico/bitacora_errores.md`](../tecnico/bitacora_errores.md).