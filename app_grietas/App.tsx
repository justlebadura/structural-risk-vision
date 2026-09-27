import React, { useState, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  StatusBar,
  SafeAreaView,
  ActivityIndicator,
  Dimensions,
  Alert,
  Modal,
  Image,
  ScrollView,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');
const FRAME_SIZE = width * 0.75;

// Endpoint HTTP de tu API local
const API_URL = 'http://192.168.1.27:8000/api/v1/cracks/analyze';

// Modelo de datos mapeado a la salida de tu arquitectura backend
interface InspectionReport {
  severity?: string; // ej: "Nivel 3 (Grave)"
  confidence?: number; // ej: 0.89
  heatmap_base64?: string; // Imagen del mapa de calor de grosor de grieta en base64
  crack_type?: string;
  recommendations?: string[];
}

export default function App() {
  const [permission, requestPermission] = useCameraPermissions();
  const [enableTorch, setEnableTorch] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [report, setReport] = useState<InspectionReport | null>(null);
  const cameraRef = useRef<any>(null);

  if (!permission) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#00E676" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#0D1117" />
        <View style={styles.permissionContent}>
          <View style={styles.iconBadge}>
            <Ionicons name="camera-outline" size={48} color="#00E676" />
          </View>
          
          <Text style={styles.permissionTitle}>Acceso a la Cámara</Text>
          <Text style={styles.permissionDescription}>
            CrackGuard requiere utilizar la cámara de tu dispositivo para capturar las imágenes e iniciar el pipeline de inspección.
          </Text>

          <TouchableOpacity
            style={styles.primaryButton}
            activeOpacity={0.8}
            onPress={requestPermission}
          >
            <Text style={styles.primaryButtonText}>Permitir Acceso</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Captura de fotografía y envío al Endpoint
// Función de captura conectada al endpoint real de FastAPI
  const handleTakePicture = async () => {
    if (cameraRef.current && !isProcessing) {
      try {
        setIsProcessing(true);

        // 1. Capturar la fotografía desde el visor
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
        });

        // 2. Preparar el archivo para enviarlo como multipart/form-data
        const formData = new FormData();
        formData.append('image', {
          uri: photo.uri,
          name: 'crack_analysis.jpg',
          type: 'image/jpeg',
        } as any);

        // 3. Petición POST a tu API en la red local
        const response = await fetch('http://192.168.1.27:8000/api/v1/cracks/analyze', {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (!response.ok) {
          throw new Error(`Error en el servidor: HTTP Status ${response.status}`);
        }

        // 4. Recibir el reporte JSON generado por el servidor
        const data: InspectionReport = await response.json();
        setReport(data);

      } catch (error) {
        console.error('Error enviando la foto al backend:', error);
        Alert.alert(
          'Error de Inspección',
          'No se pudo conectar con el servidor backend. Revisa que tu API esté en ejecución en la red local.'
        );
      } finally {
        setIsProcessing(false);
      }
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />

      {/* 1. Visor de Cámara en el Fondo */}
      <CameraView
        style={StyleSheet.absoluteFill}
        facing="back"
        enableTorch={enableTorch}
        ref={cameraRef}
      />

      {/* 2. Capa de Interfaz Flotante por encima */}
      <View style={styles.overlayContainer} pointerEvents="box-none">
        <SafeAreaView style={styles.safeArea}>
          {/* Cabecera */}
          <View style={styles.header}>
            <View style={styles.brandBadge}>
              <Text style={styles.brandTitle}>CRACKGUARD</Text>
            </View>

            <TouchableOpacity
              style={[styles.iconButton, enableTorch && styles.iconButtonActive]}
              onPress={() => setEnableTorch((prev) => !prev)}
            >
              <Ionicons
                name={enableTorch ? 'flash' : 'flash-off-outline'}
                size={22}
                color={enableTorch ? '#0D1117' : '#FFFFFF'}
              />
            </TouchableOpacity>
          </View>

          {/* Guía Visual con Marcador */}
          <View style={styles.guideContainer}>
            <View style={styles.guideFrame}>
              <View style={[styles.corner, styles.topLeft]} />
              <View style={[styles.corner, styles.topRight]} />
              <View style={[styles.corner, styles.bottomLeft]} />
              <View style={[styles.corner, styles.bottomRight]} />
            </View>
            <Text style={styles.guideText}>Encuadra la grieta y el marcador ArUco</Text>
          </View>

          {/* Botón Obturador para tomar la foto */}
          <View style={styles.footer}>
            <TouchableOpacity
              style={styles.shutterOuter}
              activeOpacity={0.7}
              onPress={handleTakePicture}
              disabled={isProcessing}
            >
              <View style={styles.shutterInner}>
                {isProcessing && <ActivityIndicator color="#0D1117" />}
              </View>
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </View>

      {/* Reporte Final Modal (Paso 8 de la arquitectura) */}
      <Modal
        visible={report !== null}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setReport(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <ScrollView contentContainerStyle={{ alignItems: 'center' }}>
              <Text style={styles.resultHeader}>Resultados de Inspección</Text>

              {/* Muestra la severidad devuelta por la red ResNet18 */}
              <View style={styles.badgeSeverity}>
                <Text style={styles.badgeSeverityText}>
                  Severidad: {report?.severity || 'Nivel Desconocido'}
                </Text>
              </View>

              {report?.confidence !== undefined && (
                <Text style={styles.resultDetail}>
                  Probabilidad (Softmax): {(report.confidence * 100).toFixed(1)}%
                </Text>
              )}

              {/* Render del Mapa de Calor si el backend devuelve la imagen procesada */}
              {report?.heatmap_base64 && (
                <View style={styles.heatmapContainer}>
                  <Text style={styles.heatmapTitle}>Mapa de Calor de Grosor:</Text>
                  <Image
                    source={{ uri: `data:image/jpeg;base64,${report.heatmap_base64}` }}
                    style={styles.heatmapImage}
                    resizeMode="contain"
                  />
                </View>
              )}

              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setReport(null)}
              >
                <Text style={styles.closeButtonText}>Nueva Inspección</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0D1117',
  },
  permissionContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  iconBadge: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: 'rgba(0, 230, 118, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(0, 230, 118, 0.2)',
  },
  permissionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 12,
    textAlign: 'center',
  },
  permissionDescription: {
    fontSize: 14,
    color: '#8B949E',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 36,
  },
  primaryButton: {
    width: '100%',
    height: 52,
    backgroundColor: '#00E676',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0D1117',
  },
  /* Capa superpuesta independiente */
  overlayContainer: {
    ...StyleSheet.absoluteFill,
    zIndex: 10,
    elevation: 10,
  },
  safeArea: {
    flex: 1,
    justifyContent: 'space-between',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 16,
  },
  brandBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(13, 17, 23, 0.75)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  brandTitle: {
    color: '#00E676',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.5,
  },
  iconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(13, 17, 23, 0.75)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  iconButtonActive: {
    backgroundColor: '#00E676',
    borderColor: '#00E676',
  },
  guideContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  guideFrame: {
    width: FRAME_SIZE,
    height: FRAME_SIZE,
    position: 'relative',
  },
  guideText: {
    marginTop: 20,
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.3,
    backgroundColor: 'rgba(13, 17, 23, 0.6)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
    overflow: 'hidden',
  },
  corner: {
    position: 'absolute',
    width: 28,
    height: 28,
    borderColor: '#00E676',
  },
  topLeft: {
    top: 0,
    left: 0,
    borderTopWidth: 3,
    borderLeftWidth: 3,
  },
  topRight: {
    top: 0,
    right: 0,
    borderTopWidth: 3,
    borderRightWidth: 3,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderBottomWidth: 3,
    borderLeftWidth: 3,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderBottomWidth: 3,
    borderRightWidth: 3,
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 32,
  },
  shutterOuter: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#00E676',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 4,
    backgroundColor: 'rgba(13, 17, 23, 0.3)',
  },
  shutterInner: {
    width: '100%',
    height: '100%',
    borderRadius: 36,
    backgroundColor: '#00E676',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    backgroundColor: '#161B22',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '80%',
    borderWidth: 1,
    borderColor: '#30363D',
  },
  resultHeader: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  badgeSeverity: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 82, 82, 0.2)',
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#FF5252',
  },
  badgeSeverityText: {
    color: '#FF5252',
    fontWeight: '700',
    fontSize: 14,
  },
  resultDetail: {
    color: '#8B949E',
    fontSize: 13,
    marginBottom: 16,
  },
  heatmapContainer: {
    width: '100%',
    alignItems: 'center',
    marginVertical: 12,
  },
  heatmapTitle: {
    color: '#C9D1D9',
    fontSize: 13,
    marginBottom: 8,
  },
  heatmapImage: {
    width: 220,
    height: 140,
    borderRadius: 8,
  },
  closeButton: {
    width: '100%',
    height: 48,
    backgroundColor: '#00E676',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  closeButtonText: {
    color: '#0D1117',
    fontWeight: '600',
    fontSize: 15,
  },
});