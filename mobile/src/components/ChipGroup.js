import { View, Text, Pressable, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';

// Groupe de puces selectionnables (meme style que la prise de RDV).
// Selection unique : value / onChange(value) — un 2e appui sur la puce active la deselectionne
// si `allowDeselect`. Selection multiple : `multiple`, values / onChange(values).
export default function ChipGroup({ options, value, values, onChange, multiple = false, allowDeselect = false }) {
  function isActive(optionValue) {
    return multiple ? values.includes(optionValue) : value === optionValue;
  }

  function handlePress(optionValue) {
    if (multiple) {
      onChange(isActive(optionValue) ? values.filter((v) => v !== optionValue) : [...values, optionValue]);
    } else {
      onChange(allowDeselect && isActive(optionValue) ? null : optionValue);
    }
  }

  return (
    <View style={styles.row} accessibilityRole={multiple ? undefined : 'radiogroup'}>
      {options.map((option) => {
        const active = isActive(option.value);
        return (
          <Pressable
            key={String(option.value)}
            onPress={() => handlePress(option.value)}
            accessibilityRole={multiple ? 'checkbox' : 'radio'}
            accessibilityState={multiple ? { checked: active } : { selected: active }}
            hitSlop={4}
            style={({ pressed }) => [styles.chip, active && styles.chipActive, pressed && styles.pressed]}
          >
            <Text style={[styles.chipText, active && styles.chipTextActive]}>
              {multiple && active ? '✓ ' : ''}
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    minHeight: 40,
    justifyContent: 'center',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  pressed: { opacity: 0.8 },
  chipText: { color: colors.text, fontWeight: '600' },
  chipTextActive: { color: '#fff' },
});
