/** Modelo de datos mapeado a la salida real del backend (core/schemas.py). */
export interface ArucoResult {
  detected: boolean;
  marker_id?: number | null;
  scale_cm_per_px?: number | null;
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

export interface InspectionReport {
  job_id?: string;
  aruco?: ArucoResult;
  preprocess?: PreprocessResult;
  filter?: FilterResult;
}