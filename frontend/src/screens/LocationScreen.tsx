import { useState } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView, StatusBar,
  ScrollView, TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { ELEMENT_OPTIONS } from '../constants/inspection';
import type { CaptureContext } from '../types/inspection';

interface LocationScreenProps {
  onConfirm: (context: CaptureContext) => void;
  onBack: () => void;
}

export function LocationScreen({ onConfirm, onBack }: LocationScreenProps) {
  const [element, setElement] = useState<string | null>(null);
  const [location, setLocation] = useState('');

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.step}>Paso 1 de 2</Text>
        <Text style={styles.title}>¿Dónde está la grieta?</Text>
        <Text style={styles.subtitle}>Selecciona el elemento estructural afectado.</Text>

        <View style={styles.grid}>
          {ELEMENT_OPTIONS.map((opt) => {
            const active = element === opt.key;
            return (
              <TouchableOpacity
                key={opt.key}
                style={[styles.chip, active && styles.chipActive]}
                activeOpacity={0.8}
                onPress={() => setElement(opt.key)}
              >
                <Ionicons name={opt.icon as any} size={22} color={active ? colors.background : colors.accent} />
                <Text style={[styles.chipText, active && styles.chipTextActive]}>{opt.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={styles.label}>Ubicación (opcional)</Text>
        <TextInput
          style={styles.input}
          placeholder="Ej.: columna C3, 1.2 m del piso"
          placeholderTextColor={colors.textSecondary}
          value={location}
          onChangeText={setLocation}
        />

        <View style={styles.actions}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>Atrás</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.nextButton, !element && styles.nextButtonDisabled]}
            disabled={!element}
            onPress={() => onConfirm({ element, location: location.trim() || null })}
          >
            <Text style={styles.nextButtonText}>Continuar</Text>
            <Ionicons name="arrow-forward" size={18} color={colors.background} />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 32 },
  step: { color: colors.accent, fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: 8 },
  title: { color: colors.textPrimary, fontSize: 22, fontWeight: '700' },
  subtitle: { color: colors.textSecondary, fontSize: 13, marginTop: 6, marginBottom: 22 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  chip: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingVertical: 12, paddingHorizontal: 14, borderRadius: 14,
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    minWidth: '47%', flexGrow: 1,
  },
  chipActive: { backgroundColor: colors.accent, borderColor: colors.accent },
  chipText: { color: colors.textPrimary, fontSize: 14, fontWeight: '600' },
  chipTextActive: { color: colors.background },
  label: { color: colors.textMuted, fontSize: 12, fontWeight: '700', letterSpacing: 1, marginTop: 26, marginBottom: 8 },
  input: {
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12,
    color: colors.textPrimary, fontSize: 14,
  },
  actions: { flexDirection: 'row', gap: 12, marginTop: 28 },
  backButton: {
    flex: 1, height: 50, borderRadius: 14, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: colors.border,
  },
  backButtonText: { color: colors.textPrimary, fontSize: 15, fontWeight: '600' },
  nextButton: {
    flex: 2, height: 50, borderRadius: 14, flexDirection: 'row', gap: 8,
    alignItems: 'center', justifyContent: 'center', backgroundColor: colors.accent,
  },
  nextButtonDisabled: { opacity: 0.4 },
  nextButtonText: { color: colors.background, fontSize: 15, fontWeight: '700' },
});