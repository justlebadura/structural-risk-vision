"""Endpoints WebSocket del backend.

Protocolo común: mensajes JSON {"type", "status", "payload"}.

- /ws/camera:   el cliente transmite frames + datos de sensor en tiempo real.
- /ws/analyze:  ejecuta el pipeline y emite progreso por etapas (secciones 1-3).
"""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services import aruco, filter as filter_svc, preprocess
from services.images import decode_base64_image

ws_router = APIRouter()


@ws_router.websocket("/ws/camera")
async def ws_camera(websocket: WebSocket) -> None:
    await websocket.accept()
    frame_count = 0
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            if data.get("type") != "frame":
                await websocket.send_json(
                    {"type": "error", "status": "bad_request", "payload": {}}
                )
                continue
            image = decode_base64_image(data.get("image", ""))
            sensor = data.get("sensor")
            stability = "estable"
            if sensor and sensor.get("rotation"):
                import numpy as np

                magnitude = float(
                    np.linalg.norm(np.asarray(sensor["rotation"], dtype=float))
                )
                from core import config

                stability = (
                    "estable" if magnitude <= config.MAX_STABILITY_DEVIATION else "inestable"
                )
            frame_count += 1
            await websocket.send_json(
                {
                    "type": "frame_ack",
                    "status": stability,
                    "payload": {"frame_count": frame_count, "received": True},
                }
            )
    except WebSocketDisconnect:
        pass


@ws_router.websocket("/ws/analyze")
async def ws_analyze(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            if data.get("type") != "analyze":
                await websocket.send_json(
                    {"type": "error", "status": "bad_request", "payload": {}}
                )
                continue

            job_id = str(uuid.uuid4())
            image = decode_base64_image(data.get("image", ""))

            await websocket.send_json(
                {"type": "progress", "status": "ok",
                 "payload": {"job_id": job_id, "step": "1_captura", "status": 0.1}}
            )

            if image is None:
                await websocket.send_json(
                    {"type": "error", "status": "invalid_image", "payload": {"job_id": job_id}}
                )
                continue

            processor = aruco.get_aruco_processor()
            await websocket.send_json(
                {"type": "progress", "status": "ok",
                 "payload": {"job_id": job_id, "step": "2_aruco", "status": 0.4}}
            )
            aruco_res = processor.detect(image)

            if not aruco_res["detected"]:
                await websocket.send_json(
                    {"type": "result", "status": "error",
                     "payload": {"job_id": job_id, "step": "2_aruco",
                                 "message": "No se detectó marcador ArUco."}}
                )
                continue

            await websocket.send_json(
                {"type": "progress", "status": "ok",
                 "payload": {"job_id": job_id, "step": "2_preprocesamiento", "status": 0.6}}
            )
            cenital = processor.warp_cenital(image, aruco_res["homography"])
            pre = preprocess.preprocess_cenital(
                cenital, aruco_res["scale_cm_per_px"], include_image=False
            )

            await websocket.send_json(
                {"type": "progress", "status": "ok",
                 "payload": {"job_id": job_id, "step": "3_filtro", "status": 0.8}}
            )
            patches = preprocess.split_patches(cenital)
            filt = filter_svc.classify_patches(patches, include_images=False)

            await websocket.send_json(
                {"type": "result", "status": "ok",
                 "payload": {"job_id": job_id, "aruco": aruco_res,
                             "preprocess": pre, "filter": filt}}
            )
    except WebSocketDisconnect:
        pass