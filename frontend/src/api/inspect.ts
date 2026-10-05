import type { InspectionReport } from '../types/inspection';

/** Endpoint HTTP de la API local. Configurable vía EXPO_PUBLIC_API_URL. */
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.27:8000';
const API_URL = `${API_BASE}/api/analyze`;

/**
 * Envía una fotografía (base64) al backend para ejecutar el pipeline
 * de inspección y devuelve el reporte generado.
 */
export async function analyzeImage(base64: string): Promise<InspectionReport> {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64 }),
  });

  if (!response.ok) {
    throw new Error(`Error en el servidor: HTTP Status ${response.status}`);
  }

  return response.json();
}