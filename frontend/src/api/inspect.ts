import type { CaptureContext, InspectionReport, SensorData } from '../types/inspection';

/** Endpoint HTTP de la API local. Configurable vía EXPO_PUBLIC_API_URL. */
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.27:8000';
const API_URL = `${API_BASE}/api/analyze`;

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
    throw new Error(`Error en el servidor: HTTP Status ${response.status}`);
  }

  return response.json();
}