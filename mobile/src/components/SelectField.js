import { useMemo, useState } from 'react';
import { View, Text, TextInput, Pressable, Modal, FlatList, StyleSheet, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../theme/colors';

function normalize(texte) {
  return texte
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim();
}

// Champ de selection avec recherche, ouvert dans une fenetre plein ecran.
// Pour les longues listes (marques, modeles, villes) : plus rapide a parcourir qu'une
// liste deroulante, et `allowCustom` permet de saisir une valeur absente de la liste.
export default function SelectField({
  label,
  value,
  options,
  onChange,
  getLabel = (v) => v,
  placeholder = 'Choisir',
  searchPlaceholder = 'Rechercher',
  disabled = false,
  disabledHint,
  allowCustom = false,
  optional = false,
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const q = normalize(query);
    if (!q) return options;
    return options.filter((o) => normalize(getLabel(o)).includes(q));
  }, [options, query, getLabel]);

  const exactMatch = options.some((o) => normalize(getLabel(o)) === normalize(query));
  const showCustom = allowCustom && query.trim().length > 0 && !exactMatch;

  function select(v) {
    onChange(v);
    setOpen(false);
    setQuery('');
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>
        {label}
        {optional ? <Text style={styles.optional}>  facultatif</Text> : null}
      </Text>
      <Pressable
        onPress={() => setOpen(true)}
        disabled={disabled}
        accessibilityRole="button"
        accessibilityLabel={`${label} : ${value ? getLabel(value) : placeholder}`}
        accessibilityHint={disabled ? disabledHint : 'Ouvre la liste de choix'}
        style={({ pressed }) => [styles.field, disabled && styles.fieldDisabled, pressed && styles.pressed]}
      >
        <Text style={[styles.value, !value && styles.placeholder]} numberOfLines={1}>
          {value ? getLabel(value) : disabled && disabledHint ? disabledHint : placeholder}
        </Text>
        <Text style={styles.chevron}>›</Text>
      </Pressable>

      <Modal
        visible={open}
        animationType="slide"
        presentationStyle={Platform.OS === 'ios' ? 'pageSheet' : 'fullScreen'}
        onRequestClose={() => setOpen(false)}
      >
        <SafeAreaView style={styles.modal} edges={['top', 'bottom']}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{label}</Text>
            <Pressable onPress={() => setOpen(false)} hitSlop={12} accessibilityRole="button">
              <Text style={styles.close}>Fermer</Text>
            </Pressable>
          </View>
          <TextInput
            style={styles.search}
            value={query}
            onChangeText={setQuery}
            placeholder={searchPlaceholder}
            placeholderTextColor={colors.textMuted}
            autoFocus
            autoCorrect={false}
            autoCapitalize="none"
            clearButtonMode="while-editing"
          />
          <FlatList
            data={filtered}
            keyExtractor={(item) => item}
            keyboardShouldPersistTaps="handled"
            initialNumToRender={20}
            ListHeaderComponent={
              showCustom ? (
                <Pressable style={styles.row} onPress={() => select(query.trim().toLowerCase())}>
                  <Text style={styles.customText}>Utiliser « {query.trim()} »</Text>
                  <Text style={styles.customHint}>Absent de la liste : l'estimation sera moins précise</Text>
                </Pressable>
              ) : null
            }
            ListEmptyComponent={
              showCustom ? null : <Text style={styles.empty}>Aucun résultat pour « {query} »</Text>
            }
            renderItem={({ item }) => {
              const selected = item === value;
              return (
                <Pressable
                  style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
                  onPress={() => select(item)}
                  accessibilityRole="button"
                  accessibilityState={{ selected }}
                >
                  <Text style={[styles.rowText, selected && styles.rowTextSelected]}>{getLabel(item)}</Text>
                  {selected ? <Text style={styles.check}>✓</Text> : null}
                </Pressable>
              );
            }}
          />
        </SafeAreaView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 14 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 6 },
  optional: { fontWeight: '400', fontStyle: 'italic' },
  field: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    minHeight: 48,
    backgroundColor: colors.surface,
  },
  fieldDisabled: { backgroundColor: colors.background },
  pressed: { opacity: 0.8 },
  value: { flex: 1, fontSize: 16, color: colors.text },
  placeholder: { color: colors.textMuted },
  chevron: { fontSize: 22, color: colors.textMuted, marginLeft: 8 },
  modal: { flex: 1, backgroundColor: colors.background },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  modalTitle: { fontSize: 18, fontWeight: '800', color: colors.text },
  close: { fontSize: 16, fontWeight: '600', color: colors.primary },
  search: {
    marginHorizontal: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
  },
  rowPressed: { backgroundColor: colors.background },
  rowText: { fontSize: 16, color: colors.text },
  rowTextSelected: { fontWeight: '700', color: colors.primary },
  check: { fontSize: 16, color: colors.primary, fontWeight: '700' },
  customText: { fontSize: 16, fontWeight: '700', color: colors.primary, width: '100%' },
  customHint: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 30 },
});
