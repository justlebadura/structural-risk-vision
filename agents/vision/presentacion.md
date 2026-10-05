# Presentación — Guion y CALL TO ACTIONS

Material para una presentación destinada a **captar atención** sobre el proyecto.
Incluye guion por diapositiva, cifras clave y **llamados a la acción**.

---

## Diapositiva 1 — Gancho

> **"¿Y si cualquier persona pudiera evaluar el riesgo de una grieta con su
> teléfono… en segundos?"**

**Structural Risk Vision** convierte una foto en un **diagnóstico estructural**:
detecta grietas, mide su grosor real y estima el **nivel de riesgo**.

---

## Diapositiva 2 — El problema

- La inspección estructural es **manual, costosa y subjetiva**.
- Puentes, edificios y obras envejecen sin monitoreo continuo.
- El diagnóstico depende de la **apreciación visual** de un experto.

**Cifra:** cada grieta no evaluada es un **riesgo latente**.

---

## Diapositiva 3 — La solución

Pipeline de **visión por computador** de 3 etapas:

1. **Captura** guiada (marcador ArUco + giróscopo).
2. **Preprocesamiento** (corrección de perspectiva + escala métrica real).
3. **Filtro binario** de grietas (U-Net ultra-ligera).

Resultado: **veredicto + vista cenital + confianza**, desde el móvil.

---

## Diapositiva 4 — El modelo (lo sorprendente)

> **Cifras en vivo:** copiar la tabla generada desde
> [`../datos/cifras_clave.md`](../datos/cifras_clave.md) (F1, ROC-AUC, parámetros,
> tamaño y latencia). No hardcodear: ese archivo se regenera con `evaluate.py`.

> Un modelo **diminuto** que clasifica grietas casi a la perfección — sin GPU,
> sin nube. **Edge AI real.**

---

## Diapositiva 5 — Rigor que da confianza

- **Matriz de confusión**, F1, recall, precisión y AUC sobre un test balanceado.
- Dataset **METU (40,000 imágenes, Özgenel)** con splits oficiales.
- EDA que distingue **datos reales de simulación** y evita conclusiones circulares.

> **Falsos negativos (grietas no vistas):** tomar el valor de
> [`../tecnico/stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md)
> (lo que más importa en seguridad).

---

## Diapositiva 6 — Por qué es interesante investigativamente

- Une **IA + ingeniería civil + geometría** (homografía, transformada de distancia).
- **Filtro rápido → segmentación → severidad**: razonamiento jerárquico eficiente.
- **Medición en milímetros reales**, no píxeles.
- Reproducible con **recursos limitados (CPU-only)**.

---

## Diapositiva 7 — Estado y hoja de ruta

- **Sprint 1 (hecho):** captura, ArUco, preprocesamiento, filtro binario + API.
- **Sprint 2 (hecho):** modelo binario entrenado (U-Net ligera), inclinación.
- **Sprint 3:** segmentación, severidad (Nivel 1–3), Grad-CAM y score de riesgo.

---

## Diapositiva 8 — Demo en vivo

1. Abrir la app móvil.
2. Enfocar una grieta + marcador ArUco.
3. Capturar → ver el **reporte** (veredicto, escala, confianza).

*(En `APP_MODE=demo` el backend responde un reporte sintético para demostrar el
flujo sin hardware.)*

---

## CALL TO ACTIONS

> Cierra con acciones **concretas y accesibles**.

### 1. Prueba la demo
```bash
cd backend && pip install -r requirements.txt && uvicorn app:app --reload
# abre http://localhost:8000/docs
```
**Acción:** ejecuta el pipeline y comparte tu resultado.

### 2. Únete al desarrollo
- Áreas abiertas: **segmentación** (sprint 3), **inclinación**, **Grad-CAM**,
  **app móvil**, **datasets**.
- Empieza por [`guias/desarrollo.md`](../guias/desarrollo.md).

### 3. Colabora con datos
- ¿Tienes fotos de grietas con **escala conocida**? Ayudan a mejorar la medición.
- Añádelas a `EDA/data/` (ver [`../datos/datasets.md`](../datos/datasets.md)).

### 4. Cita y difunde
- Comparte el repo, cita el dataset (Özgenel, 2019) y da ⭐ al proyecto.

### 5. Contacta / colabora
- ¿Investigación, docencia o aplicación industrial? **Hablemos.**
- Ideas y mejoras: abre un **issue**.

---

## Mensaje final

> **"Cada estructura merece ser evaluada antes de fallar. Y hoy, eso cabe en un
> teléfono."**

**Structural Risk Vision** — visión de riesgo estructural, abierta y reproducible.

---

## Anexo — Cifras listas para citar

> Cifras generadas automáticamente (no hardcodear). Fuente:
> [`cifras_clave.md`](../datos/cifras_clave.md),
> [`metricas.json`](../datos/metricas.json) y
> [`stats_modelo_binario.md`](../tecnico/stats_modelo_binario.md).

- F1 / Recall / ROC-AUC de la U-Net ligera → ver `cifras_clave.md`.
- Tamaño, parámetros y latencia → ver `cifras_clave.md`.
- Dataset **40,000** imágenes (METU) · test balanceado.
- Pipeline de **3 secciones** · **8 endpoints** REST · **2 WebSockets**.