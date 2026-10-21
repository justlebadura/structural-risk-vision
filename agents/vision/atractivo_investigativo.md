# Atractivo Investigativo

Por qué **Structural Risk Vision** es un proyecto con valor académico y técnico,
y qué preguntas abre.

## 1. Problema con impacto real

La **inspección estructural** de puentes, edificios y obras civiles es hoy
manual, costosa y subjetiva. Un sistema de visión por computador que detecte y
**cuantifique** grietas en tiempo real desde un teléfono móvil puede:

- Democratizar la inspección (no requiere equipo especializado).
- Reducir costos y riesgos de acceso a estructuras.
- Objetivar el diagnóstico (métricas reproducibles, no apreciación visual).

## 2. Aportes técnicos originales

### 2.1 Escala métrica real con ArUco
El pipeline **corrige la perspectiva (homografía)** usando un marcador ArUco y
deriva la **escala cm/píxel**, de modo que el grosor de la grieta se mide en
**milímetros reales**, no en píxeles. Esto conecta la visión por computador con
criterios de ingeniería civil.

### 2.2 Filtro rápido ultra-ligero (U-Net de ~122k parámetros)
Una **U-Net muy ligera** clasifica parches de 64×64 con un **F1 ≈ 1.0** en test y
un peso de unos cientos de KB. Demuestra que no hace falta un modelo enorme para
esta tarea, habilitando inferencia **en el dispositivo** (edge).
> Cifras exactas y actualizadas: [`../datos/cifras_clave.md`](../datos/cifras_clave.md).

### 2.3 Pipeline multietapa eficiente
El filtro rápido descarta parches sanos **antes** de la etapa costosa
(segmentación/severidad), reduciendo cómputo. Es una arquitectura de
**razonamiento jerárquico**: de lo barato a lo caro.

### 2.4 Inclinación aparente del elemento
Canny + Hough detecta las rectas dominantes del elemento y estima su desviación
respecto al eje vertical/horizontal, con confianza basada en la longitud de las
rectas inlier. Es una primera medición geométrica explicable que se integra al
reporte sin depender del modelo de grietas.

### 2.5 Severidad por transformada de distancia
El grosor de la grieta se estima con la **transformada de distancia** sobre la
máscara segmentada y se mapea a niveles de riesgo (Nivel 1–3), alineando la
salida con normativas de inspección.

### 2.6 Rigor metodológico en el EDA
Los cuadernos distinguen explícitamente **datos reales vs simulación** y evitan
razonamientos circulares (la severidad se testea contra el grosor **medido**, no
se deriva de él). Es un ejemplo de **honestidad de datos** en ML académico.

## 3. Preguntas de investigación abiertas

- ¿Cómo **generaliza** un modelo entrenado en fotos de cerca (METU) a la vista
  **cenital corregida** del pipeline real? (transferencia de dominio)
- ¿Cuál es el **trade-off** óptimo entre tamaño del modelo y F1 en edge?
- ¿Cómo integrar **incertidumbre** (Grad-CAM, calibración) para decisiones de riesgo?
- ¿La **medición métrica** (mm) es estable ante iluminación/ángulo?
- ¿Cómo **fusionar** clasificación binaria + segmentación + inclinación en un
  score de riesgo único y explicable?

## 4. Diferenciadores frente a trabajos típicos

| Trabajo típico | Este proyecto |
|----------------|---------------|
| Clasifica grieta/no-grieta | Estima **riesgo** (nivel) con escala métrica real |
| Modelo pesado en la nube | **Filtro ligero** apto para móvil (cientos de KB) |
| Un solo modelo | **Pipeline multietapa** (ArUco → filtro → segmentación → severidad) |
| EDA sobre datos simulados sin avisar | EDA **honesto** (real vs simulación etiquetado) |
| API monolítica | **Backend + frontend + WebSocket** documentados y con contrato claro |

## 5. Relevancia académica y de transferencia

- Aplica **visión por computador, ML y geometría (homografía)** a un problema de
  ingeniería civil.
- Producido con recursos limitados (**CPU-only**), lo que lo hace **reproducible**
  y accesible para otros estudiantes.
- Documentación pensada para **colaboración entre agentes de IA y humanos**
  (`agents/`), un aporte metodológico en sí mismo.

## 6. Métricas que respaldan el interés

Cifras generadas automáticamente desde
[`metricas.json`](../datos/metricas.json) — ver
[`cifras_clave.md`](../datos/cifras_clave.md) y
[`estadisticas.csv`](../datos/estadisticas.csv):

- **F1 ≈ 1.0** y **ROC-AUC ≈ 1.0** en test balanceado.
- Modelo de **~cientos de KB** y **unos pocos ms/parche** en CPU (U-Net ligera).
- Dataset de **40,000 imágenes** (METU, Özgenel) con splits oficiales.
- **3 secciones** de pipeline (+ inclinación 2b), **9 endpoints REST** + **2 WebSockets**.