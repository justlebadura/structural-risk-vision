import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView, StatusBar } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';

interface PermissionViewProps {
  onRequestPermission: () => void;
}

export function PermissionView({ onRequestPermission }: PermissionViewProps) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <View style={styles.content}>
        <View style={styles.iconBadge}>
          <Ionicons name="camera-outline" size={48} color={colors.accent} />
        </View>

        <Text style={styles.title}>Acceso a la Cámara</Text>
        <Text style={styles.description}>
          CrackGuard requiere utilizar la cámara de tu dispositivo para capturar las imágenes e
          iniciar el pipeline de inspección.
        </Text>

        <TouchableOpacity style={styles.primaryButton} activeOpacity={0.8} onPress={onRequestPermission}>
          <Text style={styles.primaryButtonText}>Permitir Acceso</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
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
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: 12,
    textAlign: 'center',
  },
  description: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 36,
  },
  primaryButton: {
    width: '100%',
    height: 52,
    backgroundColor: colors.accent,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.background,
  },
});