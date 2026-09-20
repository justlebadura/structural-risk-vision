# Reto: Grietas, inclinación y riesgo en edificaciones
**Algoritmos y Programación 2026-2**  
**Universidad Industrial de Santander (UIS)**  
**Facultad:** Fisicomecánicas  
**Programa Académico:** Ingeniería en Inteligencia Artificial  
**Profesor:** Jheyston Omar Serrano (jheyston@uis.edu.co)  
**Fecha de elaboración:** 12 de agosto de 2026  

---

## 1. Introducción

Las grietas en muros, columnas, vigas y placas son uno de los primeros indicadores visibles del estado de salud de una edificación. Aunque muchas son superficiales y de origen estético, otras revelan asentamientos diferenciales, sobrecargas, corrosión del refuerzo o daño estructural que, de no atenderse a tiempo, comprometen la seguridad de las personas. A esto se suma la inclinación o desaplome de muros, columnas y vigas, que suele delatar asentamientos diferenciales o pandeo y es, junto con las grietas, una de las señales de alarma más relevantes. En un país sísmico como Colombia y en ciudades con alto porcentaje de construcción informal como Barrancabermeja, contar con herramientas accesibles para el diagnóstico temprano tiene un impacto directo en la prevención de riesgos.

La inteligencia artificial, y en particular la visión por computador, permite hoy automatizar la detección y clasificación de grietas a partir de simples fotografías, incluso desde un teléfono celular. Este proyecto propone un reto de la mejor implementación: cada equipo debe construir, entrenar y desplegar un modelo de clasificación de imágenes que, a partir de fotografías de grietas y de la medición de la inclinación de los elementos estructurales, apoye la estimación del nivel de riesgo de una edificación.

---

## 2. Competencias de aprendizaje (Algoritmos y Programación)

* Aplica conocimientos de álgebra lineal, cálculo y métodos numéricos para la solución de problemas mediante programación (representación de imágenes como matrices/tensores, operaciones vectorizadas, funciones de activación y error).
* Identifica que la complejidad computacional de las soluciones algorítmicas tiene un impacto económico y ambiental, y afecta la viabilidad de ejecutar un modelo en un computador o en un celular (tamaño del modelo, tiempo de inferencia, consumo de memoria y energía).
* Identifica variables, conceptos y aspectos importantes del problema para desarrollar algoritmos que permitan su solución.
* Reconoce problemas de sistemas y organizaciones susceptibles de ser tratados algorítmicamente (diagnóstico estructural asistido por IA).
* Comunica efectivamente a diversas audiencias los conceptos, problemas y propuestas de solución de ingeniería.
* Trabaja en equipo, estableciendo objetivos y asumiendo diferentes roles para planear y ejecutar las actividades de solución de problemas.
* Investiga y selecciona fuentes confiables y relevantes de información (datasets, artículos y documentación técnica) para adquirir el conocimiento que necesita.

---

## 3. Objetivos

### Objetivo general
Diseñar, entrenar y desplegar un modelo de clasificación de imágenes que, a partir de fotografías de grietas en edificaciones y de la estimación de la inclinación de elementos estructurales (edificio, columnas y vigas), permita clasificarlas y apoyar la estimación de un nivel de riesgo estructural, ejecutando el modelo en un computador o en un teléfono celular y comprendiendo todo el proceso: captura, análisis, entrenamiento y despliegue, sobre bases de datos libres ya clasificadas.

### Objetivos específicos
1. Buscar y seleccionar una base de datos libre de imágenes de grietas ya etiquetada, comprendiendo cómo se capturaron y clasificaron los datos.
2. Analizar y preparar las imágenes (exploración, redimensionamiento, normalización y aumentación) para el entrenamiento.
3. Entrenar un modelo de clasificación (preferiblemente por transfer learning) y evaluarlo con métricas adecuadas.
4. Estimar la inclinación o desaplome de elementos estructurales mediante visión por computador (detección de líneas) y/o el sensor de inclinación del celular.
5. Desplegar el modelo entrenado en un computador o celular y probarlo con imágenes propias capturadas por el equipo.
6. Traducir la clasificación a una recomendación de nivel de riesgo y analizar la complejidad y las limitaciones de la solución.

---

## 4. Descripción del reto

El reto consiste en desarrollar un prototipo funcional de extremo a extremo (*end-to-end*) que recorra las cinco etapas del ciclo de un sistema de visión por computador. Cada equipo (3-5 estudiantes) elige su dataset del menú de la Sección 5 y construye su propia solución.

* **Etapa 1: Captura y comprensión de los datos.** Seleccionar una base de datos libre ya clasificada y entender su origen. Capturar un conjunto propio de fotografías de prueba.
* **Etapa 2: Análisis y preprocesamiento de imágenes.** Explorar el dataset, representar la imagen como matriz/tensor, redimensionar, normalizar y aplicar aumentación de datos. Separar en entrenamiento, validación y prueba.
* **Etapa 3: Entrenamiento de la red.** Entrenar un modelo de clasificación (Transfer Learning con MobileNet V2 o EfficientNet-Lite sobre TensorFlow/Keras o PyTorch).
* **Etapa 4: Evaluación e interpretación.** Medir desempeño (exactitud, precisión, *recall*, F1, matriz de confusión) y métricas de complejidad (parámetros, tamaño en MB, tiempo de inferencia).
* **Etapa 5: Despliegue.** Poner el modelo en funcionamiento en un celular (TensorFlow Lite / Edge Impulse) o en un computador (Streamlit / Gradio).

### Del resultado al riesgo
* **Nivel base:** Clasificación binaria con/sin grieta e inclinación gruesa.
* **Nivel intermedio:** Clasificación del tipo de grieta u orientación y ángulo de desaplome.
* **Nivel avanzado:** Estimación de nivel de riesgo (bajo/medio/alto) combinando predicciones con reglas simples de ingeniería.

---

## 5. Menú de bases de datos libres

| Dataset | Tarea | Descripción y Acceso |
| :--- | :--- | :--- |
| **Concrete Crack Images (METU / Özgenel)** | Binaria | ~40,000 imágenes $227\times227$ en 2 clases (con/sin grieta). Ideal para empezar y para móvil. [Kaggle Surface Crack Detection](https://www.kaggle.com/datasets/arunrk7/surface-crack-detection) / Mendeley Data. |
| **SDNET2018** | Binaria | ~56,000 imágenes anotadas de concreto (puentes, muros y pavimentos), con y sin grieta. Utah State University. |
| **CODEBRIM** | Multi-etiqueta | Imágenes de defectos en concreto: grieta, descascaramiento, eflorescencia, refuerzo expuesto y corrosión. |
| **Crack Forest (CFD) / Crack 500 / Deep Crack** | Segmentación | Datasets con máscaras de grietas a nivel de píxel (nivel avanzado/opcional). |

---

## 6. Herramientas sugeridas

* **Entrenamiento:** Google Colab (GPU gratuita), Python, TensorFlow/Keras o PyTorch.
* **Sin código:** Teachable Machine (Google) y Edge Impulse.
* **Inclinación / visión clásica:** OpenCV (detección Canny y Hough) y sensores del celular.
* **Despliegue móvil:** TensorFlow Lite / LiteRT.
* **Despliegue PC/web:** Streamlit o Gradio.
* **Datos y colaboración:** Roboflow, Git/GitHub.

---

## 7. Fechas de evaluación (Periodo 2026-2)

* **CORTE 1 (Semana 8 - 25/09/2026):** 20%
* **CORTE 2 (Semana 12 - 23/10/2026):** 20%
* **CORTE 3 (Semana 16 - 20/11/2026):** 30%

---

## 8. Actividades y entregables

* **Entrega 1 (Corte 1 - 25/09/2026):** Formulación del problema, selección del dataset, análisis exploratorio, prototipo funcional inicial de extremo a extremo (clasificador base + inclinación con OpenCV/sensor) y repositorio en GitHub con roles del equipo.
* **Entrega 2 (Corte 2 - 23/10/2026):** Cuaderno documentado con preprocesamiento, mejora por *transfer learning*, métricas, análisis de complejidad e integración de módulos.
* **Entrega 3 (Corte 3 - 20/11/2026):** Modelo desplegado (app móvil o web), mapeo a nivel de riesgo, análisis de limitaciones, informe técnico final y sustentación con demostración en vivo.

---

## 9. Criterio de "la mejor implementación"

| Criterio | Peso |
| :--- | :--- |
| Desempeño del modelo (métricas en prueba y fotos propias) | 30% |
| Despliegue funcional en computador o celular (usabilidad) | 25% |
| Eficiencia y complejidad (tamaño, inferencia, viabilidad móvil) | 15% |
| Comprensión del pipeline completo y calidad del análisis (ética/limitaciones) | 20% |
| Comunicación, documentación y trabajo en equipo | 10% |

---

## 10. Enlaces y recursos de interés
* [Concrete Crack Images en Kaggle](https://www.kaggle.com/datasets/arunrk7/surface-crack-detection)
* [Concrete Crack Images en Mendeley Data](https://data.mendeley.com/datasets/5y9wdsg2zt/2)
* [SDNET2018](https://digitalcommons.usu.edu/all_datasets/48/)
* [CODEBRIM](https://zenodo.org/record/2620293)
* [Teachable Machine](https://teachablemachine.withgoogle.com/)
* [Edge Impulse](https://edgeimpulse.com/)
* [TensorFlow Lite / LiteRT](https://ai.google.dev/edge/litert)
* [Tutorial de líneas de Hough en OpenCV](https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html)
* [Reglamento Colombiano de Construcción Sismo Resistente (NSR-10)](https://www.culturarecreacionydeporte.gov.co/sites/default/files/reglamento_construccion_sismo_resistente.pdf)