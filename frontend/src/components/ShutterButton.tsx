import { StyleSheet, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { colors } from '../theme/colors';

interface ShutterButtonProps {
  onPress: () => void;
  disabled?: boolean;
  processing?: boolean;
}

export function ShutterButton({ onPress, disabled, processing }: ShutterButtonProps) {
  return (
    <View style={styles.wrapper}>
      <TouchableOpacity
        style={styles.outer}
        activeOpacity={0.7}
        onPress={onPress}
        disabled={disabled}
      >
        <View style={styles.inner}>{processing && <ActivityIndicator color={colors.background} />}</View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
    paddingBottom: 32,
  },
  outer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 4,
    backgroundColor: colors.glass,
  },
  inner: {
    width: '100%',
    height: '100%',
    borderRadius: 36,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
});