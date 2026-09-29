"""Endpoints REST del backend.

Todos los endpoints devuelven schemas definidos en core.schemas, que son el
único contrato que consume el frontend (ver /docs).
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from core import config
from core.schemas import (
    ArucoDetection,
    CameraStatus,
    CaptureRequest,
    FilterResult,
    ModelInfo,
    PreprocessResult,
    AnalyzeResponse,
    TrainingConfig,
    TrainingStatus,
)
from services import aruco, camera, filter as filter_svc, preprocess, training

router = APIRouter(prefix="/api", tags=["api"])

# Sesiones de cámara activas (memoria; en prod usar un store externo).
_sessions: dict[str, camera.CameraSession] = {}


def _get_session(session_id: Optional[str]) -> camera.CameraSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    raise HTTPException(status_code=404, detail="Sesión de cámara no encontrada.")


# ---------------------------------------------------------------------------
# Salud
# ---------------------------------------------------------------------------
@router.get("/health", response_model=dict)
def health() -> dict:
    from core.model_loader import get_filter_model

    model = get_filter_model()
    return {
        "status": "ok",
        "mode": config.APP_MODE,
        "filter_backend": model.backend,
        "sections": {"1_captura": True, "2_preprocesamiento": True, "3_filtro": True},
        "filter_model": "loaded" if model.present else "pending",
        "filter_model_path": str(config.FILTER_MODEL_PATH),
    }


# ---------------------------------------------------------------------------
# Modelo y entrenamiento del filtro binario
# ---------------------------------------------------------------------------
@router.get("/model/status", response_model=ModelInfo)
def model_status() -> ModelInfo:
    from core.model_loader import get_filter_model

    model = get_filter_model()
    size = None
    if config.FILTER_MODEL_PATH.exists():
        size = config.FILTER_MODEL_PATH.stat().st_size
    return ModelInfo(
        mode=config.APP_MODE,
        backend=model.backend,
        model_present=model.present,
        model_path=str(config.FILTER_MODEL_PATH),
        size_bytes=size,
    )


@router.post("/model/upload", response_model=ModelInfo)
async def model_upload(file: UploadFile = File(...)) -> ModelInfo:
    """Sube un modelo .tflite entrenado y lo recarga como filtro real."""
    if not file.filename or not file.filename.endswith(".tflite"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .tflite.")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    data = await file.read()
    config.FILTER_MODEL_PATH.write_bytes(data)

    from core.model_loader import reload_filter_model

    model = reload_filter_model()
    return ModelInfo(
        mode=config.APP_MODE,
        backend=model.backend,
        model_present=model.present,
        model_path=str(config.FILTER_MODEL_PATH),
        size_bytes=len(data),
    )


@router.get("/training/status", response_model=TrainingStatus)
def training_status() -> TrainingStatus:
    return TrainingStatus(**training.get_training_service().status())


@router.post("/training/start", response_model=TrainingStatus)
def training_start(cfg: Optional[TrainingConfig] = None) -> TrainingStatus:
    params = cfg.dict(exclude_none=True) if cfg else {}
    return TrainingStatus(**training.get_training_service().start(params))


@router.post("/training/stop", response_model=TrainingStatus)
def training_stop() -> TrainingStatus:
    return TrainingStatus(**training.get_training_service().stop())


# ---------------------------------------------------------------------------
# Sección 1 - Captura
# ---------------------------------------------------------------------------
@router.post("/camera/start", response_model=CameraStatus)
def camera_start() -> CameraStatus:
    session = camera.start_session()
    _sessions[session.session_id] = session
    return CameraStatus(
        active=True, session_id=session.session_id, frame_count=0
    )


@router.post("/camera/stop", response_model=CameraStatus)
def camera_stop(session_id: str = Query(...)) -> CameraStatus:
    session = _get_session(session_id)
    session.stop()
    _sessions.pop(session_id, None)
    return CameraStatus(active=False, session_id=session_id)


@router.post("/capture", response_model=dict)
def capture(req: CaptureRequest, session_id: str = Query(...)) -> dict:
    """Registra un frame del cliente + datos de sensor en la sesión."""
    session = _get_session(session_id)
    image = _decode(req.image)
    sensor = req.sensor.dict() if req.sensor else None
    state = session.feed(image, sensor)
    return {"session_id": session_id, "frame_count": session.frame_count, **state}


# ---------------------------------------------------------------------------
# Sección 2 - ArUco y preprocesamiento
# ---------------------------------------------------------------------------
@router.post("/aruco/detect", response_model=ArucoDetection)
def aruco_detect(req: CaptureRequest) -> ArucoDetection:
    image = _decode(req.image)
    if image is None:
        raise HTTPException(status_code=400, detail="Imagen inválida o vacía.")
    sensor = req.sensor.dict() if req.sensor else None
    stability = None
    if sensor and sensor.get("rotation"):
        stability = _evaluate_stability(sensor)
    result = aruco.get_aruco_processor().detect(image, sensor_stability=stability)
    return ArucoDetection(**result)


@router.post("/preprocess", response_model=PreprocessResult)
def preprocess_endpoint(req: CaptureRequest) -> PreprocessResult:
    """Detecta ArUco y devuelve la vista cenital + escala + parches."""
    image = _decode(req.image)
    if image is None:
        raise HTTPException(status_code=400, detail="Imagen inválida o vacía.")

    aruco_res = aruco.get_aruco_processor().detect(image)
    if not aruco_res["detected"]:
        raise HTTPException(
            status_code=422,
            detail="No se detectó marcador ArUco para corregir perspectiva.",
        )

    cenital = aruco.get_aruco_processor().warp_cenital(image, aruco_res["homography"])
    result = preprocess.preprocess_cenital(
        cenital, aruco_res["scale_cm_per_px"], include_image=True
    )
    return PreprocessResult(**result)


# ---------------------------------------------------------------------------
# Sección 3 - Filtro rápido
# ---------------------------------------------------------------------------
@router.post("/filter", response_model=FilterResult)
def filter_endpoint(req: CaptureRequest) -> FilterResult:
    """Corre el filtro binario sobre los parches de la imagen cenital."""
    image = _decode(req.image)
    if image is None:
        raise HTTPException(status_code=400, detail="Imagen inválida o vacía.")

    aruco_res = aruco.get_aruco_processor().detect(image)
    if not aruco_res["detected"]:
        raise HTTPException(
            status_code=422,
            detail="No se detectó marcador ArUco para el filtro rápido.",
        )

    cenital = aruco.get_aruco_processor().warp_cenital(image, aruco_res["homography"])
    patches = preprocess.split_patches(cenital)
    result = filter_svc.classify_patches(patches, include_images=False)
    return FilterResult(**result)


# ---------------------------------------------------------------------------
# Pipeline completo (secciones 1-3)
# ---------------------------------------------------------------------------
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: CaptureRequest) -> AnalyzeResponse:
    """Encadena captura(1) + ArUco/preprocesamiento(2) + filtro(3)."""
    image = _decode(req.image)
    if image is None:
        raise HTTPException(status_code=400, detail="Imagen inválida o vacía.")

    sensor = req.sensor.dict() if req.sensor else None
    stability = None
    if sensor and sensor.get("rotation"):
        stability = _evaluate_stability(sensor)

    processor = aruco.get_aruco_processor()
    aruco_res = processor.detect(image, sensor_stability=stability)
    aruco_out = ArucoDetection(**aruco_res)

    preprocess_out = None
    filter_out = None
    if aruco_res["detected"]:
        cenital = processor.warp_cenital(image, aruco_res["homography"])
        preprocess_out = PreprocessResult(
            **preprocess.preprocess_cenital(
                cenital, aruco_res["scale_cm_per_px"], include_image=True
            )
        )
        patches = preprocess.split_patches(cenital)
        filter_out = FilterResult(**filter_svc.classify_patches(patches))

    return AnalyzeResponse(
        job_id=str(uuid.uuid4()),
        aruco=aruco_out,
        preprocess=preprocess_out,
        filter=filter_out,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _decode(image_b64: str):
    from services.images import decode_base64_image

    return decode_base64_image(image_b64)


def _evaluate_stability(sensor: dict) -> str:
    rot = sensor.get("rotation") or []
    import numpy as np

    magnitude = float(np.linalg.norm(np.asarray(rot, dtype=float)))
    return "estable" if magnitude <= config.MAX_STABILITY_DEVIATION else "inestable"