import type { CaptureContext, HealthResponse, InspectionReport, SensorData } from '../types/inspection';

/** Endpoint HTTP de la API local. Configurable vía EXPO_PUBLIC_API_URL. */
export const API_BASE = (process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const API_URL = `${API_BASE}/api/analyze`;

/** Consulta el estado del backend y del modelo de inferencia. */
export async function getHealth(timeoutMs = 6000): Promise<HealthResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE}/api/health`, { signal: controller.signal });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Envía una fotografía (base64) + sensores + contexto de ubicación al backend
 * para ejecutar el pipeline de inspección y devuelve el reporte generado.
 */
export async function analyzeImage(
  base64: string,
  sensor?: SensorData,
  context?: CaptureContext
): Promise<InspectionReport> {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64, sensor: sensor ?? null, context: context ?? null }),
  });

  if (!response.ok) {
    throw new Error(`Error en ${API_URL}: HTTP ${response.status}`);
  }

  return response.json();
}