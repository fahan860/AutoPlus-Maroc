import { View, Text, Pressable, StyleSheet, ScrollView, Linking } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import PrimaryButton from '../../components/PrimaryButton';
import { CATEGORIES_PANNE, URGENCES, categorieLabel } from '../../utils/pannes';
import { formatThousands } from '../../utils/vehicleLabels';
import { colors } from '../../theme/colors';

function DiagnosticCard({ categories, panne }) {
  const principale = categories[0];
  const urgence = panne?.urgence ? URGENCES[panne.urgence] : null;
  const autres = categories.slice(1);
  return (
    <View style={styles.diagnostic}>
      <Text style={styles.diagLabel}>Problème probable</Text>
      <View style={styles.diagRow}>
        <Text style={styles.diagIcon}>{CATEGORIES_PANNE[principale?.categorie]?.icon ?? '🔧'}</Text>
        <View style={styles.flexShrink}>
          <Text style={styles.diagTitle}>{categorieLabel(principale?.categorie)}</Text>
          {panne ? <Text style={styles.diagPanne}>{panne.titre}</Text> : null}
        </View>
      </View>

      <View style={styles.diagTags}>
        {urgence ? (
          <View style={[styles.tag, { backgroundColor: urgence.fond }]}>
            <Text style={[styles.tagText, { color: urgence.couleur }]}>{urgence.label}</Text>
          </View>
        ) : null}
        {panne?.cout_min_dh != null && panne?.cout_max_dh != null ? (
          <View style={[styles.tag, styles.tagNeutral]}>
            <Text style={styles.tagText}>
              Coût indicatif : {formatThousands(panne.cout_min_dh)} – {formatThousands(panne.cout_max_dh)} DH
            </Text>
          </View>
        ) : null}
      </View>

      {autres.length > 0 ? (
        <Text style={styles.diagOthers}>Aussi possible : {autres.map((c) => categorieLabel(c.categorie)).join(', ')}</Text>
      ) : null}
      <Text style={styles.diagDisclaimer}>Diagnostic indicatif : le garagiste confirmera sur place.</Text>
    </View>
  );
}

function GarageRecoCard({ garage, rang, onOpen }) {
  return (
    <View style={styles.card}>
      <Pressable onPress={onOpen} accessibilityRole="button" accessibilityLabel={`Voir le garage ${garage.nom}`}>
        <View style={styles.cardHeader}>
          <View style={[styles.rank, rang === 1 && styles.rankFirst]}>
            <Text style={[styles.rankText, rang === 1 && styles.rankTextFirst]}>{rang}</Text>
          </View>
          <View style={styles.flexShrink}>
            <Text style={styles.cardTitle}>{garage.nom}</Text>
            {garage.adresse ? <Text style={styles.cardAddress} numberOfLines={1}>{garage.adresse}</Text> : null}
          </View>
        </View>

        <View style={styles.reasons}>
          {garage.raisons.map((raison) => (
            <Text key={raison} style={styles.reason}>✓ {raison}</Text>
          ))}
        </View>
        {!garage.specialites_confirmees ? (
          <Text style={styles.unconfirmed}>Spécialités non encore confirmées par le garage</Text>
        ) : null}
      </Pressable>

      <View style={styles.cardActions}>
        {garage.telephone ? (
          <Pressable
            style={({ pressed }) => [styles.actionButton, pressed && styles.pressed]}
            onPress={() => Linking.openURL(`tel:${garage.telephone.replace(/\s/g, '')}`)}
            accessibilityRole="button"
            accessibilityLabel={`Appeler ${garage.nom}`}
          >
            <Text style={styles.actionText}>📞 Appeler</Text>
          </Pressable>
        ) : null}
        <Pressable
          style={({ pressed }) => [styles.actionButton, styles.actionPrimary, pressed && styles.pressed]}
          onPress={onOpen}
          accessibilityRole="button"
        >
          <Text style={[styles.actionText, styles.actionTextPrimary]}>Voir / RDV ›</Text>
        </Pressable>
      </View>
    </View>
  );
}

export default function RecommendedGaragesScreen({ navigation, route }) {
  const insets = useSafeAreaInsets();
  const { resultat, description, positionRefusee } = route.params;
  const { categories_probables: categories, pannes_proches: pannes, garages, avertissements } = resultat;

  return (
    <ScrollView
      style={styles.flex}
      contentContainerStyle={[styles.content, { paddingBottom: Math.max(insets.bottom, 16) + 8 }]}
    >
      <Text style={styles.quote} numberOfLines={3}>« {description} »</Text>

      <DiagnosticCard categories={categories} panne={pannes[0]} />

      {avertissements.map((a) => (
        <View key={a} style={styles.warning}>
          <Text style={styles.warningText}>ⓘ {a}</Text>
          {positionRefusee && a.startsWith('Position inconnue') ? (
            <Pressable
              style={({ pressed }) => [styles.warningAction, pressed && styles.pressed]}
              onPress={() => Linking.openSettings()}
              accessibilityRole="button"
            >
              <Text style={styles.warningActionText}>Autoriser la localisation dans les réglages ›</Text>
            </Pressable>
          ) : null}
        </View>
      ))}

      <Text style={styles.sectionTitle}>
        {garages.length > 0 ? `Garages recommandés (${garages.length})` : 'Aucun garage trouvé'}
      </Text>

      {garages.length === 0 ? (
        <Text style={styles.empty}>
          Aucun garage référencé ne traite encore ce type de panne. Consultez la liste complète des garages.
        </Text>
      ) : (
        garages.map((garage, i) => (
          <GarageRecoCard
            key={garage.id}
            garage={garage}
            rang={i + 1}
            onOpen={() => navigation.navigate('GarageDetail', { garageId: garage.id })}
          />
        ))
      )}

      <View style={styles.footerActions}>
        <PrimaryButton title="Modifier la description" variant="outline" onPress={() => navigation.goBack()} />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  flexShrink: { flexShrink: 1 },
  content: { padding: 16 },
  quote: { fontSize: 14, fontStyle: 'italic', color: colors.textMuted, marginBottom: 12, paddingHorizontal: 4 },
  diagnostic: { backgroundColor: colors.primary, borderRadius: 16, padding: 18, marginBottom: 12 },
  diagLabel: { color: '#D6E4F0', fontSize: 13, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8 },
  diagRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8 },
  diagIcon: { fontSize: 32, marginRight: 12 },
  diagTitle: { color: '#fff', fontSize: 22, fontWeight: '800' },
  diagPanne: { color: '#D6E4F0', fontSize: 14, marginTop: 2, lineHeight: 19 },
  diagTags: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 14 },
  tag: { borderRadius: 12, paddingHorizontal: 10, paddingVertical: 5 },
  tagNeutral: { backgroundColor: '#fff' },
  tagText: { fontSize: 13, fontWeight: '700', color: colors.text },
  diagOthers: { color: '#D6E4F0', fontSize: 13, marginTop: 12 },
  diagDisclaimer: { color: '#AFC6DB', fontSize: 12, marginTop: 8, fontStyle: 'italic' },
  warning: { backgroundColor: '#FEF5E7', borderColor: '#F8C471', borderWidth: 1, borderRadius: 12, padding: 12, marginBottom: 10 },
  warningText: { color: colors.text, fontSize: 13, lineHeight: 19 },
  warningAction: { marginTop: 8, alignSelf: 'flex-start', minHeight: 32, justifyContent: 'center' },
  warningActionText: { color: colors.primary, fontWeight: '700', fontSize: 14 },
  sectionTitle: { fontSize: 18, fontWeight: '800', color: colors.text, marginTop: 6, marginBottom: 10 },
  empty: { color: colors.textMuted, lineHeight: 20, marginBottom: 12 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center' },
  rank: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  rankFirst: { backgroundColor: colors.accent, borderColor: colors.accent },
  rankText: { fontWeight: '800', color: colors.textMuted },
  rankTextFirst: { color: '#fff' },
  cardTitle: { fontSize: 16, fontWeight: '800', color: colors.text },
  cardAddress: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  reasons: { marginTop: 10, gap: 3 },
  reason: { fontSize: 14, color: colors.text },
  unconfirmed: { fontSize: 12, color: colors.textMuted, fontStyle: 'italic', marginTop: 6 },
  cardActions: { flexDirection: 'row', gap: 10, marginTop: 12 },
  actionButton: {
    flex: 1,
    minHeight: 44,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionPrimary: { backgroundColor: colors.primary },
  pressed: { opacity: 0.8 },
  actionText: { fontWeight: '700', color: colors.primary },
  actionTextPrimary: { color: '#fff' },
  footerActions: { marginTop: 4 },
});
