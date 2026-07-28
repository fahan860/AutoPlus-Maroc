import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';

const REQUIREMENTS = [
  { label: 'Au moins 8 caractères', test: (value) => value.length >= 8 },
  { label: 'Une majuscule', test: (value) => /[A-Z]/.test(value) },
  { label: 'Une minuscule', test: (value) => /[a-z]/.test(value) },
  { label: 'Un chiffre', test: (value) => /\d/.test(value) },
  { label: 'Un caractère spécial', test: (value) => /[^A-Za-z0-9]/.test(value) },
];

export function isPasswordValid(value) {
  return REQUIREMENTS.every((req) => req.test(value));
}

export default function PasswordRequirements({ password }) {
  return (
    <View style={styles.container}>
      {REQUIREMENTS.map((req) => {
        const met = req.test(password);
        return (
          <View key={req.label} style={styles.row}>
            <Text style={[styles.icon, met && styles.iconMet]}>{met ? '✓' : '○'}</Text>
            <Text style={[styles.label, met && styles.labelMet]}>{req.label}</Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginTop: -4, marginBottom: 14 },
  row: { flexDirection: 'row', alignItems: 'center', marginTop: 4 },
  icon: {
    width: 16,
    fontSize: 13,
    fontWeight: '700',
    color: colors.textMuted,
  },
  iconMet: { color: colors.success },
  label: { fontSize: 12, color: colors.textMuted },
  labelMet: { color: colors.success, fontWeight: '600' },
});
