"""Entrypoint del backend FastAPI.

Levanta la aplicación, monta los routers REST y WebSocket y habilita CORS
para que el frontend (que desarrolla otra persona) se conecte desde cualquier
origen en desarrollo. El frontend consume únicamente el OpenAPI en /docs.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router as rest_router
from api.ws import ws_router

app = FastAPI(
    title="Structural Risk Vision - Backend",
    description=(
        "Backend del sistema de detección de grietas e inclinación estructural.\n"
        "Sprint 1 implementa las secciones 1-3 del Documento de Arquitectura "
        "Optimizada: Captura (ArUco + giróscopo), Preprocesamiento (perspectiva "
        "y escala real) y Filtro rápido (clasificación binaria).\n\n"
        "Contrato del frontend: este OpenAPI (/docs)."
    ),
    version="0.1.0",
)

# CORS abierto en desarrollo (el frontend corre en otro origen).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router)
app.include_router(ws_router)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "service": "Structural Risk Vision API",
        "docs": "/docs",
        "redoc": "/redoc",
        "sprint": 1,
        "sections": "1-3",
    }