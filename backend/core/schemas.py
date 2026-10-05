"""Schemas Pydantic (contrato de API).

Estos modelos definen exactamente lo que el frontend recibe. Son el único
contrato que consume la interfaz (ver /docs OpenAPI generado por FastAPI).
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Sección 1 - Captura
# ---------------------------------------------------------------------------
class SensorData(BaseModel):
    """Datos del giróscopo/acelerómetro que el cliente envía con cada frame."""
    rotation: Optional[List[float]] = None   # [rx, ry, rz] rad/s
    accel: Optional[List[float]] = None      # [ax, ay, az] m/s^2 (incluye gravedad)


class CaptureContext(BaseModel):
    """Información aportada por el usuario sobre la ubicación de la grieta."""
    element: Optional[str] = None    # "columna" | "viga" | "muro" | "losa" | "piso" | "techo" | ...
    location: Optional[str] = None   # descripción libre (p. ej. "columna C3, 1.2 m")
    notes: Optional[str] = None      # observaciones adicionales


class CaptureRequest(BaseModel):
    image: str                       # frame en base64
    sensor: Optional[SensorData] = None
    context: Optional[CaptureContext] = None


class CameraStatus(BaseModel):
    active: bool
    session_id: Optional[str] = None
    frame_count: int = 0
    last_capture_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Sección 2 - ArUco + preprocesamiento
# ---------------------------------------------------------------------------
class ArucoDetection(BaseModel):
    detected: bool
    marker_id: Optional[int] = None
    corners: Optional[List[List[float]]] = None   # 4 esquinas [[x, y], ...]
    homography: Optional[List[List[float]]] = None
    scale_cm_per_px: Optional[float] = None
    tilt_deg: Optional[float] = None              # inclinación del marcador (grados)
    roll_deg: Optional[float] = None              # rotación en el plano de imagen
    cenital_ok: Optional[bool] = None             # True si la perspectiva es aceptable
    orientation: Optional[str] = None             # "cenital_ok" | "angulo_incorrecto"
    stability: Optional[str] = None               # "estable" | "inestable"
    message: Optional[str] = None


class PreprocessResult(BaseModel):
    cenital_image: Optional[str] = None   # imagen corregida base64
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    scale_cm_per_px: Optional[float] = None
    total_patches: Optional[int] = None


# ---------------------------------------------------------------------------
# Sección 3 - Filtro rápido (clasificación binaria)
# ---------------------------------------------------------------------------
class PatchResult(BaseModel):
    patch: Optional[str] = None      # base64 del parche
    probability: float               # P(grieta) en [0, 1]
    label: str                       # "GRIETA" | "NO_GRIETA"


class FilterResult(BaseModel):
    implemented: bool                # True si el .tflite está cargado
    model_present: bool              # True si existe el archivo .tflite
    total_patches: int
    crack_patches: int
    no_crack_patches: int
    verdict: str                     # "GRIETA" | "NO_GRIETA" | "SIN_MODELO"
    confidence: Optional[float] = None
    patches: List[PatchResult] = []


# ---------------------------------------------------------------------------
# Pipeline completo (secciones 1-3)
# ---------------------------------------------------------------------------
class AnalyzeResponse(BaseModel):
    job_id: str
    aruco: ArucoDetection
    preprocess: Optional[PreprocessResult] = None
    filter: Optional[FilterResult] = None
    # Contexto de la inspección (Sección 1)
    surface: Optional[str] = None            # "techo" | "piso" | "pared" | "indeterminado"
    surface_tilt_deg: Optional[float] = None # ángulo del dispositivo respecto a la horizontal
    element: Optional[str] = None            # elemento indicado por el usuario (columna, viga…)
    location: Optional[str] = None           # ubicación en texto libre