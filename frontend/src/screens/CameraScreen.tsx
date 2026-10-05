import { useState, useRef } from 'react';
import { StyleSheet, View, StatusBar, ActivityIndicator, Alert } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { colors } from '../theme/colors';
import { analyzeImage } from '../api/inspect';
import type { InspectionReport } from '../types/inspection';
import { PermissionView } from '../components/PermissionView';
import { CameraOverlay } from '../components/CameraOverlay';
import { ShutterButton } from '../components/ShutterButton';
import { ResultModal } from '../components/ResultModal';

export function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [torchOn, setTorchOn] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [report, setReport] = useState<InspectionReport | null>(null);
  const cameraRef = useRef<any>(null);

  if (!permission) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  if (!permission.granted) {
    return <PermissionView onRequestPermission={requestPermission} />;
  }

  const handleTakePicture = async () => {
    if (cameraRef.current && !isProcessing) {
      try {
        setIsProcessing(true);

        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: true,
        });

        if (!photo.base64) {
          throw new Error('No se pudo codificar la imagen a base64.');
        }

        const data = await analyzeImage(photo.base64);
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

      <CameraView
        style={StyleSheet.absoluteFill}
        facing="back"
        enableTorch={torchOn}
        ref={cameraRef}
      />

      {/* Capa de interfaz flotante por encima del visor */}
      <View style={styles.overlay} pointerEvents="box-none">
        <CameraOverlay torchOn={torchOn} onToggleTorch={() => setTorchOn((prev) => !prev)} />
        <ShutterButton onPress={handleTakePicture} disabled={isProcessing} processing={isProcessing} />
      </View>

      <ResultModal report={report} onClose={() => setReport(null)} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  overlay: {
    ...StyleSheet.absoluteFill,
    zIndex: 10,
    elevation: 10,
    justifyContent: 'space-between',
  },
});