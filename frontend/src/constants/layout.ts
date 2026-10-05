import { Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

/** Tamaño del cuadrado guía (marcador ArUco) en pantalla. */
export const FRAME_SIZE = width * 0.75;