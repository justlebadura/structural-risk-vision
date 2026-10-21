# Bitácora de errores, imprecisiones y decisiones

Registro de los problemas que encontramos, cómo los detectamos, qué decidimos
y qué queda pendiente. La idea no es ocultar los errores, sino dejar trazable
el razonamiento experimental.

## 1. Resumen de incidentes

| # | Problema | Cómo se detectó | Decisión aplicada | Estado |
|---|----------|-----------------|-------------------|--------|
| 1 | EDA podía parecer real usando datos sintéticos | Revisión del notebook y salidas sin etiqueta clara | Fallback de simulación etiquetado en pantalla + EDA real ejecutado con METU | Resuelto |
| 2 | Los notebooks no tenían salidas versionadas | `01` tenía 0/10 celdas con salida y `execution_count=None` | Ejecución con `nbconvert` y commit del `.ipynb` con salidas | Resuelto |
| 3 | Cargar 40,000 imágenes agotaba la RAM | Cálculo de memoria: ~6.2 GB solo en píxeles | Muestra estratificada de 2,000/clase + conteos completos sin cargar imágenes | Resuelto para revisión; dataset completo pendiente |
| 4 | Severidad tautológica en el notebook 02 | La severidad se derivaba del grosor y luego se correlacionaba con él | Etiqueta de severidad independiente con ruido; test de asociación no circular | Resuelto |
| 5 | Bins de LBP incorrectos | Un LBP uniforme con P=8 tiene P+2=10 patrones, no 8 | Histograma con 10 bins | Resuelto |
| 6 | El modelo confunde sombras duras con grietas | Experimento controlado con sombras sintéticas sobre METU | Análisis en EDA + recomendación de captura + corrección BGR→RGB | Mitigado y documentado; reentrenamiento pendiente |
| 7 | El backend pasaba parches BGR a un modelo entrenado en RGB | Revisión del flujo `decode_base64 → patches → BinaryModel` | Conversión explícita `BGR→RGB` en `services/filter.py` y scripts | Resuelto |
| 8 | Inclinación del marcador confundida con inclinación del elemento | El campo `tilt_deg` era del ArUco, no del elemento | Nuevo `services/inclination.py` con Canny + Hough y campo separado | Resuelto con alcance 2D |
| 9 | `APP_MODE=demo` podía mostrar resultados sintéticos como si fueran reales | El reporte no indicaba el modo de ejecución | `mode`/`demo` en la respuesta + badge en la app + aviso `SIN_MODELO` | Resuelto |
| 10 | MobileNetV2 mostraba sobreajuste leve | `val_loss` subía tras la mejor época | Se desplegó U-Net ligera por F1, tamaño y estabilidad | Resuelto |
| 11 | Umbral óptimo calculado en test podía ser leakage | `evaluate.py` busca el mejor umbral sobre test | Se mantiene 0.5 para producción; los umbrales óptimos se reportan solo como diagnóstico | Documentado |
| 12 | F1 ≈ 1.0 podía leerse como “problema resuelto” | METU está casi saturado (>99% en literatura) | Se documenta la saturación y se prioriza el dominio real (vista cenital) | Documentado |
| 13 | Test y train de METU pueden compartir foto-fuente | METU genera 40k parches desde 458 fotos | Se reporta la limitación y se usa validación como control; split por fuente pendiente | Pendiente |
| 14 | `tflite_runtime` no siempre está disponible | Fallo de importación en el entorno local | `BinaryModel` cae a `tf.lite.Interpreter` como fallback | Resuelto |

## 2. Caso detallado: sombras duras y falsos positivos

### Qué pasó

En el dominio real, una sombra proyectada con un borde recto puede parecerse a
una grieta: ambas son una transición oscura y alargada. El modelo se entrenó con
METU, un dataset de grietas de cerca, sin un protocolo explícito de sombras.

### Cómo lo medimos

Se tomó una muestra balanceada de **300 imágenes por clase** del set de test de
METU y se aplicaron tres variantes:

1. `base`: imagen original.
2. `sombra_suave`: gradiente lateral suave, como luz difusa.
3. `sombra_dura`: mitad de la imagen oscurecida con borde recto.
4. `sombra_dura_clahe`: sombra dura + CLAHE.
5. `base_clahe`: imagen original + CLAHE.

Resultados del cuaderno `01_clasificacion_grietas.ipynb` (modelo TFLite desplegado):

| Escenario | Accuracy | Recall | Specificity | FPR | FN | FP |
|-----------|----------|--------|-------------|-----|----|----|
| base | 0.9750 | 0.9667 | 0.9833 | 0.0167 | 10 | 5 |
| sombra_suave | 0.9683 | 0.9533 | 0.9833 | 0.0167 | 14 | 5 |
| sombra_dura | 0.5067 | 1.0000 | 0.0133 | **0.9867** | 0 | **296** |
| sombra_dura_clahe | 0.5883 | 0.9967 | 0.1800 | 0.8200 | 1 | 246 |
| base_clahe | 0.9617 | 0.9700 | 0.9533 | 0.0467 | 9 | 14 |

### Interpretación

- La **sombra suave** no inventa grietas: el FPR se mantiene en 1.67%, pero el
  recall baja de 96.67% a 95.33% (más falsos negativos).
- La **sombra dura** sí rompe el modelo: el FPR sube a **98.67%** y solo 4 de
  300 imágenes sanas se clasifican correctamente como sanas.
- **CLAHE** reduce el FPR de 98.67% a 82.00%, pero sigue siendo inaceptable y
  empeora la especificidad en imágenes normales (98.33% → 95.33%). Por eso no se
  activó por defecto.

### Decisiones

1. **No se activó CLAHE** como preprocesamiento de inferencia: mitiga un caso
   patológico a costa de degradar el caso normal.
2. **Se corrigió el orden de canales** en inferencia (`BGR→RGB`). El modelo se
   entrenó con RGB, pero el backend recibía BGR de OpenCV. Es un error sutil que
   puede afectar la respuesta a color/iluminación.
3. **Se añadió una recomendación de captura** en la app: evitar sombras duras y
   usar luz difusa.
4. **Se dejó la augmentación de sombras como línea de reentrenamiento**. No se
   aplicó al modelo desplegado para no presentar métricas de un modelo distinto
   sin reentrenar y reevaluar.
5. **Se dejó el experimento como prueba de regresión**: cualquier modelo futuro
   debe reportar FPR bajo sombra dura, no solo F1 en METU.

## 3. Caso: BGR vs RGB

### Qué pasó

El flujo del backend decodifica la imagen con OpenCV en **BGR**, la rectifica y
la divide en parches. `BinaryModel.predict()` recibía esos parches BGR, pero
`data.py` entrena con **RGB**. El modelo aprendió colores en un orden y en
producción veía otro.

### Decisión

- `services/filter.py` convierte cada parche a RGB antes de predecir.
- `verificar_inferencia.py` también convierte antes de la prueba.
- El contrato del modelo sigue siendo RGB; el backend es quien adapta su
  representación interna.

## 4. Caso: EDA aparentemente real

### Qué pasó

El primer notebook podía caer en un fallback sintético sin que el lector viera
con claridad que los resultados no eran de METU. Además, el notebook 01 no
tenía salidas versionadas.

### Decisión

- El notebook imprime un bloque explícito de **MODO SIMULACIÓN** cuando no hay
  datos reales.
- Se ejecutó con METU real (muestra 2,000/clase) y se versionaron las salidas.
- Se documentó `EDA_SAMPLE_PER_CLASS` para reproducir la muestra o ejecutar el
  dataset completo con `0`.
- El notebook 02 sigue en simulación porque no hay máscaras reales de
  segmentación; se etiqueta como tal y no se presentan sus cifras como hallazgos
  de Crack500/CFD.

## 5. Caso: severidad tautológica

### Qué pasó

En una versión inicial, la severidad se asignaba a partir del grosor medido y
luego se correlacionaba con ese mismo grosor. La correlación era
matemáticamente esperada, no un hallazgo.

### Decisión

- La severidad se asigna como etiqueta de referencia independiente (con ruido).
- Se mide el grosor con transformada de distancia de forma separada.
- Se reporta Spearman entre la etiqueta y el grosor medido, sabiendo que no es
  circular.

## 6. Caso: bins de LBP

### Qué pasó

Un LBP uniforme con `P=8` produce `P+2 = 10` patrones. Usar 8 bins perdía dos
patrones y distorsionaba el histograma.

### Decisión

`N_BINS = n_points + 2` y el histograma se normaliza. Queda documentado en el
notebook 01.

## 7. Caso: métricas saturadas y fuga de fuente

METU reporta >99% en literatura. Un F1 de 0.9976 no significa que el problema
esté resuelto:

- METU son 40,000 parches derivados de solo 458 fotos.
- Test y train pueden compartir la misma foto-fuente.
- El dominio real del pipeline es la vista cenital de una foto móvil, no un
  recorte de METU.

Decisiones:

- No se usa el F1 de METU como métrica única.
- Se reporta la limitación en `stats_modelo_binario.md` y en el README.
- Se usa el set de validación como control.
- El split por foto-fuente y la evaluación en dominio real quedan pendientes.

## 8. Caso: umbral 0.5 vs umbral óptimo

`evaluate.py` calcula el umbral que maximiza F1 en test (0.54 para U-Net, 0.26
para MobileNetV2). Usar ese umbral en producción sería leakage: se eligió con
los mismos datos con los que se reporta.

Decisión:

- Producción usa `FILTER_THRESHOLD=0.5`, un valor neutro y no ajustado a test.
- Los umbrales óptimos se reportan solo como diagnóstico.
- Si en el futuro se calibra un umbral, debe hacerse con un conjunto de
  calibración separado.

## 9. Caso: MobileNetV2 y sobreajuste leve

MobileNetV2 obtuvo F1 0.9974, pero su `val_loss` subió después de la mejor época
y no activó early stopping (paró en la época 18). Además pesa 1.6 MB frente a
492 KB de la U-Net y tiene 411,489 parámetros frente a 121,883.

Decisión:

- Se desplegó la **U-Net ligera**: mejor F1, mucho menor tamaño y sin señal de
  sobreajuste.
- MobileNetV2 queda como baseline y como alternativa si en el futuro la latencia
  es el cuello de botella.

## 10. Caso: inclinación del marcador vs inclinación del elemento

`aruco.estimate_tilt_deg()` estima la inclinación del **plano del marcador**
respecto a la cámara. Eso no es la inclinación de la columna o viga.

Decisión:

- Se separó el concepto en `services/inclination.py`.
- Se añadió Canny + Hough para la inclinación aparente del elemento.
- Se documenta que es una medida **2D respecto al eje de la imagen**, no una
  medida absoluta con inclinómetro.
- La validación se hizo con METU y una escena sintética; no hay fotos propias de
  campo.

## 11. Qué queda pendiente

1. Reentrenar con augmentación de sombras duras y suaves y volver a medir el FPR.
2. Evaluar el modelo en la vista cenital real (dominio del pipeline), no solo en
   METU.
3. Construir un split por foto-fuente para reducir la fuga de METU.
4. Validar la inclinación con fotos propias y una referencia geométrica conocida.
5. Calibrar un umbral con un conjunto separado, si se decide cambiar el 0.5.
