# Documento de Arquitectura Optimizada: Sistema de Inspección de Grietas

Este documento presenta la arquitectura rediseñada para el sistema de inspección de grietas, incorporando soluciones directas a problemas críticos de entrada multicanal, mitigación de desbalance de clases, explicabilidad y propagación de errores.

## 1. Captura | Marcador ArUco + Guía por giróscopo
* **Descripción:** Adquisición de la imagen en campo mediante smartphone, asistida por el marcador ArUco para corrección geométrica y sensores inerciales para asegurar estabilidad y ángulo de captura óptimo.

## 2. Preprocesamiento | Corrección de perspectiva y escala real
* **Descripción:** Normalización geométrica de la imagen utilizando los vértices del marcador ArUco para transformar la perspectiva a una vista cenital uniforme y calibrar los píxeles a unidades métricas reales (cm/píxel).

## 3. Filtro rápido | Clasificador de parches, descarta sin grieta
* **Descripción:** División de la imagen normalizada en parches (ej. 64x64) evaluados por un clasificador ligero para descartar rápidamente zonas de fondo sano y optimizar el cómputo posterior.

## 4. Segmentación semántica | FPN o U-Net con MobileNet (Transfer Learning)
* **Descripción:** Red de segmentación basada en un backbone MobileNet preentrenado que procesa los parches seleccionados y genera una máscara binaria precisa (256x256) de la fisura.

## 5. Postproceso geométrico | Generación de la Transformada de Distancia
* **Descripción:** Aplicación del bloque de transformada de distancia sobre la máscara binaria para producir un mapa de calor métrico, donde los colores cálidos representan mayor grosor/apertura y los fríos menor grosor.

## 6. Fusión Multicanal y Clasificación Convolucional | ResNet18 Modificada (RGB + Heatmap)
* **Modificación Estructural Crítica:** Se reemplaza la primera capa convolucional de una ResNet18 preentrenada en ImageNet para aceptar un tensor de 4 canales ($256 \times 256 \times 4$), compuesto por los 3 canales RGB de la imagen original más el mapa de calor de distancia de 1 canal.
* **Transfer Learning Híbrido:** Los pesos de los primeros 3 canales se heredan de ImageNet (aprovechando texturas, humedad y color del sustrato), mientras que el cuarto canal se inicializa ponderando los pesos existentes.
* **Flujo Robusto:** La red analiza conjuntamente la geometría y el contexto visual bruto, previniendo la dependencia ciega de la máscara binaria.

## 7. Salida Multiclase con Focal Loss y Softmax
* **Estrategia de Desbalance:** Entrenamiento optimizado mediante la función de pérdida Focal Loss y muestreo ponderado para evitar sesgos hacia las clases leves (Nivel 1), garantizando sensibilidad robusta frente a casos críticos (Nivel 3).
* **Clasificación Final:** Capa Softmax que arroja probabilidades discretas para Nivel 1 (Leve), Nivel 2 (Moderada) y Nivel 3 (Grave/Crítica).

## 8. Módulo de Explicabilidad con Grad-CAM
* **Transparencia en Decisiones de Riesgo:** Generación automática de mapas de activación Grad-CAM extraídos de las capas profundas de la ResNet18 modificada.
* **Trazabilidad Visual:** Superposición gráfica sobre la imagen RGB original para evidenciar exactamente qué patrón visual o anomalía impulsó la clasificación de severidad crítica.

## 9. Reporte final | Despliegue integral
* **Descripción:** Interfaz móvil final que muestra al operador la categoría de severidad predicha, el nivel de confianza, el mapa de calor geométrico y el mapa de explicabilidad Grad-CAM para validación de campo.