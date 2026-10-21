"""Sección 2b - Inclinación aparente del elemento con Canny + Hough.

Detecta las rectas dominantes de un elemento estructural (columna, viga, muro,
losa...) y estima su desviación respecto al eje esperado **en el plano de la
imagen**:

- columna / muro / pilar -> eje vertical (90°),
- viga / losa / piso / techo -> eje horizontal (0°),
- cualquier otro elemento -> se elige el eje más cercano a las rectas.

No es un inclinómetro: la medición es relativa al eje de la imagen (o al
marcador ArUco si la captura está rectificada). Para obtener una inclinación
absoluta respecto a la gravedad haría falta una referencia externa.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from core import config

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


VERTICAL_ELEMENTS = {"columna", "pilar", "muro", "pared"}
HORIZONTAL_ELEMENTS = {"viga", "losa", "piso", "techo"}


def _expected_axis(element: Optional[str]) -> Optional[float]:
    """Devuelve 90° para elementos verticales, 0° para horizontales o None."""
    key = (element or "").strip().lower()
    if key in VERTICAL_ELEMENTS:
        return 90.0
    if key in HORIZONTAL_ELEMENTS:
        return 0.0
    return None


def detect_lines(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Devuelve las rectas detectadas por Canny + HoughLinesP."""
    if cv2 is None or image is None:
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    median = float(np.median(gray))
    lower = int(max(0, config.CANNY_LOW_RATIO * median))
    upper = int(min(255, config.CANNY_HIGH_RATIO * median))
    edges = cv2.Canny(gray, lower, upper, apertureSize=3)

    h, w = gray.shape[:2]
    min_side = min(h, w)
    min_line = max(20, int(min_side * config.HOUGH_MIN_LINE_LENGTH_RATIO))
    max_gap = max(5, int(min_side * config.HOUGH_MAX_LINE_GAP_RATIO))

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=config.HOUGH_THRESHOLD,
        minLineLength=min_line,
        maxLineGap=max_gap,
    )
    if lines is None:
        return []
    return [tuple(int(v) for v in line[0]) for line in lines]


def _line_angle_deg(x1: int, y1: int, x2: int, y2: int) -> float:
    """Ángulo del eje de la recta en [0, 180)."""
    return float(math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180.0)


def _signed_delta(angle: float, axis: float) -> float:
    """Diferencia angular con signo en [-90, 90) respecto a un eje."""
    return float(((angle - axis + 90.0) % 180.0) - 90.0)


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cumulative = np.cumsum(weights)
    return float(values[int(np.searchsorted(cumulative, cumulative[-1] / 2.0))])


def detect_element_inclination(
    image: np.ndarray,
    element: Optional[str] = None,
) -> dict:
    """Estima la inclinación aparente del elemento en la imagen.

    Devuelve un dict compatible con el schema `ElementInclination`.
    """
    base = {
        "detected": False,
        "method": "canny_hough",
        "tilt_deg": None,
        "tilt_signed_deg": None,
        "angle_deg": None,
        "reference": None,
        "confidence": 0.0,
        "lines_count": 0,
        "inlier_lines": 0,
        "reliable": False,
        "message": "OpenCV no disponible." if cv2 is None else "Sin rectas suficientes.",
    }
    if cv2 is None or image is None:
        return base

    lines = detect_lines(image)
    base["lines_count"] = len(lines)
    if len(lines) < config.INCLINATION_MIN_LINES:
        base["message"] = (
            f"Se detectaron {len(lines)} rectas; se necesitan al menos "
            f"{config.INCLINATION_MIN_LINES} para estimar la inclinación."
        )
        return base

    expected = _expected_axis(element)
    angles = np.array([_line_angle_deg(*line) for line in lines], dtype=float)
    lengths = np.array(
        [math.hypot(line[2] - line[0], line[3] - line[1]) for line in lines],
        dtype=float,
    )
    valid = lengths > 0
    angles, lengths = angles[valid], lengths[valid]
    if len(angles) == 0:
        return base

    # Sin contexto, el eje esperado es el más cercano al ángulo dominante.
    if expected is None:
        vertical_delta = np.abs(np.array([_signed_delta(a, 90.0) for a in angles]))
        horizontal_delta = np.abs(np.array([_signed_delta(a, 0.0) for a in angles]))
        vertical_weight = float(lengths[vertical_delta <= config.INCLINATION_AXIS_TOLERANCE_DEG].sum())
        horizontal_weight = float(lengths[horizontal_delta <= config.INCLINATION_AXIS_TOLERANCE_DEG].sum())
        expected = 90.0 if vertical_weight >= horizontal_weight else 0.0
        reference = "auto"
    else:
        reference = "vertical" if expected == 90.0 else "horizontal"

    deltas = np.array([_signed_delta(a, expected) for a in angles])
    inliers = np.abs(deltas) <= config.INCLINATION_AXIS_TOLERANCE_DEG
    if inliers.sum() < config.INCLINATION_MIN_LINES:
        base["message"] = "No hay suficientes rectas alineadas con el eje esperado."
        return base

    weights = lengths[inliers]
    # La mediana ponderada evita que una grieta diagonal arrastre el resultado.
    tilt_signed = _weighted_median(deltas[inliers], weights)
    confidence = float(weights.sum() / lengths.sum()) if lengths.sum() > 0 else 0.0
    reliable = confidence >= config.INCLINATION_MIN_CONFIDENCE

    base.update(
        {
            "detected": True,
            "tilt_deg": round(abs(tilt_signed), 2),
            "tilt_signed_deg": round(tilt_signed, 2),
            "angle_deg": round((expected + tilt_signed) % 180.0, 2),
            "reference": reference,
            "confidence": round(confidence, 4),
            "inlier_lines": int(inliers.sum()),
            "reliable": bool(reliable),
            "message": (
                "Inclinación estimada con Canny + Hough."
                if reliable
                else "Inclinación estimada con confianza baja; mejora el encuadre."
            ),
        }
    )
    return base


def draw_overlay(
    image: np.ndarray,
    lines: list[tuple[int, int, int, int]],
    result: dict,
) -> np.ndarray:
    """Dibuja las rectas detectadas y el resultado sobre una copia de la imagen."""
    if image is None:
        return image
    out = image.copy()
    if cv2 is None:
        return out

    for x1, y1, x2, y2 in lines:
        cv2.line(out, (x1, y1), (x2, y2), (0, 220, 120), 2, cv2.LINE_AA)

    if result.get("detected"):
        text = (
            f"Inclinacion: {result['tilt_deg']:.1f} deg "
            f"({result.get('reference')}, conf. {result.get('confidence', 0):.0%})"
        )
        cv2.putText(out, text, (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 220, 120), 2, cv2.LINE_AA)
    return out
