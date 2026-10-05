import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView, StatusBar, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';

interface MenuScreenProps {
  onStart: () => void;
}

const STEPS = [
  { icon: 'location-outline', text: 'Indica dónde está la grieta (columna, viga, muro…)' },
  { icon: 'scan-outline', text: 'Encuadra la grieta junto al marcador ArUco' },
  { icon: 'analytics-outline', text: 'Obtén el veredicto y la vista cenital' },
] as const;

export function MenuScreen({ onStart }: MenuScreenProps) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.logoBadge}>
          <Ionicons name="shield-checkmark" size={40} color={colors.accent} />
        </View>
        <Text style={styles.brand}>CRACKGUARD</Text>
        <Text style={styles.subtitle}>Visión de riesgo estructural</Text>
        <Text style={styles.description}>
          Detecta grietas en concreto, mide su grosor real y estima el nivel de riesgo.
        </Text>

        <TouchableOpacity style={styles.primaryButton} activeOpacity={0.85} onPress={onStart}>
          <Ionicons name="camera" size={20} color={colors.background} />
          <Text style={styles.primaryButtonText}>Nueva inspección</Text>
        </TouchableOpacity>

        <View style={styles.steps}>
          <Text style={styles.stepsTitle}>¿Cómo funciona?</Text>
          {STEPS.map((s, i) => (
            <View key={s.text} style={styles.stepRow}>
              <View style={styles.stepIcon}>
                <Ionicons name={s.icon as any} size={18} color={colors.accent} />
              </View>
              <Text style={styles.stepText}>
                <Text style={styles.stepNum}>{i + 1}. </Text>
                {s.text}
              </Text>
            </View>
          ))}
        </View>
      </ScrollView>
      <Text style={styles.footer}>Proyecto académico · UIS</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { flexGrow: 1, justifyContent: 'center', alignItems: 'center', padding: 28 },
  logoBadge: {
    width: 88, height: 88, borderRadius: 44, alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(0, 230, 118, 0.1)', borderWidth: 1, borderColor: 'rgba(0, 230, 118, 0.25)',
    marginBottom: 20,
  },
  brand: { color: colors.accent, fontSize: 24, fontWeight: '800', letterSpacing: 3 },
  subtitle: { color: colors.textPrimary, fontSize: 15, fontWeight: '600', marginTop: 6 },
  description: {
    color: colors.textSecondary, fontSize: 13, textAlign: 'center',
    lineHeight: 20, marginTop: 10, marginBottom: 28, maxWidth: 320,
  },
  primaryButton: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    width: '100%', maxWidth: 340, height: 54, backgroundColor: colors.accent, borderRadius: 16,
  },
  primaryButtonText: { color: colors.background, fontSize: 16, fontWeight: '700' },
  steps: { width: '100%', maxWidth: 340, marginTop: 32 },
  stepsTitle: { color: colors.textMuted, fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: 12 },
  stepRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  stepIcon: {
    width: 34, height: 34, borderRadius: 17, alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(0, 230, 118, 0.08)', marginRight: 12,
  },
  stepText: { color: colors.textSecondary, fontSize: 13, flex: 1, lineHeight: 18 },
  stepNum: { color: colors.accent, fontWeight: '700' },
  footer: { color: colors.textSecondary, fontSize: 11, textAlign: 'center', paddingBottom: 16 },
});