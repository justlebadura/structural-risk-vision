"""Genera una predicción concreta y reproducible del pipeline completo.

Construye una escena sintética de inspección a partir de una grieta real de
METU + un marcador ArUco generado en el momento, ejecuta las etapas del
backend (ArUco, cenital, parches, filtro TFLite e inclinación Canny+Hough) y
guarda la entrada, la salida JSON y una imagen anotada.

Uso:
    python backend/scripts/prediccion_ejemplo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core import config  # noqa: E402
from model.model_binary.data import list_split  # noqa: E402
from services import aruco, filter as filter_svc, inclination, preprocess  # noqa: E402

OUT_DIR = REPO_ROOT / "agents" / "datos" / "ejemplo_prediccion"
SIZE = 640
MARKER_PX = 110
MARKER_MARGIN = 28


def _metu_crack() -> Path:
    items = list_split("test", n_per_class=1, seed=42)
    return next(path for path, label in items if label == 1)


def _build_scene(texture_path: Path) -> np.ndarray:
    texture = cv2.imread(str(texture_path))
    if texture is None:
        raise FileNotFoundError(f"No se pudo leer {texture_path}")
    scene = cv2.resize(texture, (SIZE, SIZE), interpolation=cv2.INTER_CUBIC)

    # Bordes del elemento (muro) con una leve inclinación de ~3°.
    cv2.line(scene, (118, 30), (88, SIZE - 20), (35, 35, 35), 6, cv2.LINE_AA)
    cv2.line(scene, (522, 30), (552, SIZE - 20), (35, 35, 35), 6, cv2.LINE_AA)

    dictionary = cv2.aruco.getPredefinedDictionary(config.MARKER_DICT_ID)
    marker = cv2.aruco.generateImageMarker(dictionary, config.MARKER_DICT_ID, MARKER_PX)
    marker = cv2.copyMakeBorder(
        marker, MARKER_MARGIN, MARKER_MARGIN, MARKER_MARGIN, MARKER_MARGIN,
        cv2.BORDER_CONSTANT, value=255,
    )
    y0 = SIZE - marker.shape[0] - 8
    x0 = SIZE - marker.shape[1] - 8
    scene[y0:y0 + marker.shape[0], x0:x0 + marker.shape[1]] = cv2.cvtColor(
        marker, cv2.COLOR_GRAY2BGR
    )
    return scene


def _filter_summary(result: dict) -> dict:
    return {
        "model_present": result.get("model_present"),
        "total_patches": result.get("total_patches"),
        "crack_patches": result.get("crack_patches"),
        "no_crack_patches": result.get("no_crack_patches"),
        "verdict": result.get("verdict"),
        "confidence": result.get("confidence"),
        "threshold": config.FILTER_THRESHOLD,
    }


def _annotate(scene: np.ndarray, cenital: np.ndarray, filt: dict, incl: dict, aruco_res: dict) -> np.ndarray:
    left = inclination.draw_overlay(scene, inclination.detect_lines(scene), incl)
    if aruco_res.get("corners"):
        pts = np.array(aruco_res["corners"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(left, [pts], True, (0, 220, 120), 2, cv2.LINE_AA)

    right = cenital.copy()
    size = config.PATCH_SIZE
    patches = filt.get("patches", [])
    for idx, patch in enumerate(patches):
        y = (idx // (right.shape[1] // size)) * size
        x = (idx % (right.shape[1] // size)) * size
        color = (0, 0, 220) if patch.get("label") == "GRIETA" else (0, 180, 80)
        cv2.rectangle(right, (x, y), (x + size, y + size), color, 1)

    verdict = filt.get("verdict", "SIN_MODELO")
    confidence = filt.get("confidence")
    text = f"Veredicto: {verdict}"
    if confidence is not None:
        text += f"  ({confidence * 100:.1f}% de parches)"
    cv2.rectangle(right, (0, 0), (right.shape[1], 42), (25, 25, 25), -1)
    cv2.putText(right, text, (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                (0, 220, 120), 2, cv2.LINE_AA)

    left = cv2.resize(left, (SIZE, SIZE))
    right = cv2.resize(right, (SIZE, SIZE))
    cv2.putText(left, "Entrada + Hough", (12, SIZE - 14), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(right, "Vista cenital + parches", (12, SIZE - 14), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return cv2.hconcat([left, right])


def main() -> int:
    image_path = _metu_crack()
    scene = _build_scene(image_path)

    processor = aruco.get_aruco_processor()
    aruco_res = processor.detect(scene)
    if not aruco_res.get("detected"):
        print("No se detectó el marcador ArUco de la escena de ejemplo.")
        return 1

    cenital = processor.warp_cenital(scene, aruco_res["homography"])
    pre = preprocess.preprocess_cenital(
        cenital, aruco_res["scale_cm_per_px"], include_image=False
    )
    patches = preprocess.split_patches(cenital)
    filt = filter_svc.classify_patches(patches, include_images=False)
    incl = inclination.detect_element_inclination(scene, element="muro")

    payload = {
        "ejemplo": "prediccion_ejemplo",
        "descripcion": (
            "Escena reproducible: textura de grieta real de METU + marcador ArUco "
            "sintético. No es una inspección de campo."
        ),
        "imagen_fuente": str(image_path.relative_to(REPO_ROOT)),
        "mode": "inferencia_directa",
        "demo": False,
        "aruco": {
            "detected": aruco_res.get("detected"),
            "marker_id": aruco_res.get("marker_id"),
            "scale_cm_per_px": aruco_res.get("scale_cm_per_px"),
            "tilt_deg": aruco_res.get("tilt_deg"),
            "cenital_ok": aruco_res.get("cenital_ok"),
        },
        "preprocess": {
            "width_cm": pre.get("width_cm"),
            "height_cm": pre.get("height_cm"),
            "scale_cm_per_px": pre.get("scale_cm_per_px"),
            "total_patches": pre.get("total_patches"),
        },
        "filter": _filter_summary(filt),
        "inclination": incl,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT_DIR / "entrada.jpg"), scene, [cv2.IMWRITE_JPEG_QUALITY, 92])
    cv2.imwrite(str(OUT_DIR / "salida.png"), _annotate(scene, cenital, filt, incl, aruco_res))
    (OUT_DIR / "salida.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
