/** Modelo de datos mapeado a la salida real del backend (core/schemas.py). */

export interface ArucoResult {
  detected: boolean;
  marker_id?: number | null;
  scale_cm_per_px?: number | null;
  tilt_deg?: number | null;
  roll_deg?: number | null;
  cenital_ok?: boolean | null;
  orientation?: string | null;
  stability?: string | null;
  message?: string | null;
}

export interface PreprocessResult {
  cenital_image?: string | null;
  width_cm?: number | null;
  height_cm?: number | null;
  scale_cm_per_px?: number | null;
  total_patches?: number | null;
}

export interface FilterResult {
  verdict?: string | null;
  confidence?: number | null;
  total_patches?: number;
  crack_patches?: number;
}

/** Información que el usuario aporta sobre la ubicación de la grieta. */
export interface CaptureContext {
  element?: string | null;
  location?: string | null;
  notes?: string | null;
}

/** Datos del giróscopo/acelerómetro enviados con la captura. */
export interface SensorData {
  rotation?: [number, number, number] | null;
  accel?: [number, number, number] | null;
}

export interface InspectionReport {
  job_id?: string;
  aruco?: ArucoResult;
  preprocess?: PreprocessResult;
  filter?: FilterResult;
  surface?: string | null;
  surface_tilt_deg?: number | null;
  element?: string | null;
  location?: string | null;
}