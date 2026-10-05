/** Opciones de ubicación estructural que el usuario elige antes de capturar. */
export interface ElementOption {
  key: string;
  label: string;
  icon: string;
}

export const ELEMENT_OPTIONS: ElementOption[] = [
  { key: 'columna', label: 'Columna', icon: 'albums-outline' },
  { key: 'viga', label: 'Viga', icon: 'remove-outline' },
  { key: 'muro', label: 'Muro / Pared', icon: 'square-outline' },
  { key: 'losa', label: 'Losa', icon: 'grid-outline' },
  { key: 'piso', label: 'Piso', icon: 'arrow-down-outline' },
  { key: 'techo', label: 'Techo', icon: 'arrow-up-outline' },
  { key: 'otro', label: 'Otro', icon: 'ellipsis-horizontal-outline' },
];