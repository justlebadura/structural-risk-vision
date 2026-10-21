import {
  StyleSheet,
  Text,
  View,
  Modal,
  Image,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import type { InspectionReport } from '../types/inspection';
import { colors } from '../theme/colors';

interface ResultModalProps {
  report: InspectionReport | null;
  onClose: () => void;
}

export function ResultModal({ report, onClose }: ResultModalProps) {
  return (
    <Modal
      visible={report !== null}
      animationType="slide"
      transparent
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.card}>
          <ScrollView contentContainerStyle={styles.cardContent}>
            <View style={styles.resultHeader}>
              <Text style={styles.resultHeaderText}>Resultados de Inspección</Text>
              {report?.aruco?.detected === false && (
                <Text style={styles.resultDetail}>{report.aruco.message}</Text>
              )}
            </View>

            {/* Modo de ejecución: demo o inferencia real */}
            <View style={[styles.badgeMode, report?.demo ? styles.badgeModeDemo : styles.badgeModeReal]}>
              <Text style={styles.badgeModeText}>
                {report?.demo ? 'Modo demo · resultado sintético' : 'Inferencia real'}
              </Text>
            </View>

            {/* Severidad según el veredicto del filtro binario */}
            <View style={styles.badgeSeverity}>
              <Text style={styles.badgeSeverityText}>
                Veredicto: {report?.filter?.verdict || 'SIN_MODELO'}
              </Text>
            </View>

            {report?.filter && report.filter.model_present === false && (
              <Text style={styles.resultWarning}>
                El modelo no está cargado en el backend. Coloca filter.tflite y usa APP_MODE=prod.
              </Text>
            )}

            {(report?.element || report?.surface) && (
              <Text style={styles.resultDetail}>
                Ubicación: {[report?.element, report?.surface, report?.location]
                  .filter(Boolean)
                  .join(' · ')}
              </Text>
            )}

            {report?.aruco?.tilt_deg !== undefined && report.aruco.tilt_deg !== null && (
              <Text style={styles.resultDetail}>
                Inclinación de captura: {report.aruco.tilt_deg.toFixed(1)}°
                {report.aruco.cenital_ok === false ? ' (perspectiva mejorable)' : ' (cenital ✓)'}
              </Text>
            )}

            {report?.inclination?.detected && report.inclination.tilt_deg !== null && report.inclination.tilt_deg !== undefined && (
              <Text style={styles.resultDetail}>
                Inclinación del elemento: {report.inclination.tilt_deg.toFixed(1)}°
                {report.inclination.reference ? ` (${report.inclination.reference})` : ''}
                {report.inclination.confidence !== null && report.inclination.confidence !== undefined
                  ? ` · confianza ${(report.inclination.confidence * 100).toFixed(0)}%`
                  : ''}
              </Text>
            )}

            {report?.inclination && !report.inclination.detected && report.inclination.message && (
              <Text style={styles.resultDetail}>
                Inclinación del elemento: {report.inclination.message}
              </Text>
            )}

            {report?.filter?.confidence !== undefined && report.filter.confidence !== null && (
              <Text style={styles.resultDetail}>
                Fracción de parches con grieta: {(report.filter.confidence * 100).toFixed(1)}%
              </Text>
            )}

            {report?.aruco?.scale_cm_per_px !== undefined && report.aruco.scale_cm_per_px !== null && (
              <Text style={styles.resultDetail}>
                Escala: {report.aruco.scale_cm_per_px.toFixed(3)} cm/píxel
              </Text>
            )}

            {/* Render de la vista cenital corregida si el backend la devuelve */}
            {report?.preprocess?.cenital_image && (
              <View style={styles.heatmapContainer}>
                <Text style={styles.heatmapTitle}>Vista Cenital Corregida:</Text>
                <Image
                  source={{ uri: `data:image/jpeg;base64,${report.preprocess.cenital_image}` }}
                  style={styles.heatmapImage}
                  resizeMode="contain"
                />
              </View>
            )}

            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Text style={styles.closeButtonText}>Nueva Inspección</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'flex-end',
  },
  card: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '80%',
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardContent: {
    alignItems: 'center',
  },
  resultHeader: {
    marginBottom: 12,
    alignItems: 'center',
  },
  resultHeaderText: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textPrimary,
    textAlign: 'center',
  },
  badgeMode: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
  },
  badgeModeDemo: {
    backgroundColor: 'rgba(255, 193, 7, 0.15)',
    borderColor: 'rgba(255, 193, 7, 0.5)',
  },
  badgeModeReal: {
    backgroundColor: 'rgba(0, 230, 118, 0.12)',
    borderColor: 'rgba(0, 230, 118, 0.4)',
  },
  badgeModeText: {
    color: colors.textPrimary,
    fontSize: 11,
    fontWeight: '700',
  },
  resultWarning: {
    color: colors.danger,
    fontSize: 12,
    lineHeight: 17,
    textAlign: 'center',
    marginBottom: 10,
  },
  badgeSeverity: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 82, 82, 0.2)',
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.danger,
  },
  badgeSeverityText: {
    color: colors.danger,
    fontWeight: '700',
    fontSize: 14,
  },
  resultDetail: {
    color: colors.textSecondary,
    fontSize: 13,
    marginBottom: 16,
  },
  heatmapContainer: {
    width: '100%',
    alignItems: 'center',
    marginVertical: 12,
  },
  heatmapTitle: {
    color: colors.textMuted,
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
    backgroundColor: colors.accent,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  closeButtonText: {
    color: colors.background,
    fontWeight: '600',
    fontSize: 15,
  },
});