import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import PrimaryButton from '../../components/PrimaryButton';
import { BOITES, CARBURANTS, ETATS, displayName, formatDh, formatThousands, labelOf } from '../../utils/vehicleLabels';
import { colors } from '../../theme/colors';

// Barre de fourchette : le prix estime positionne entre le minimum et le maximum
function RangeBar({ min, max, prix }) {
  const position = max > min ? Math.min(Math.max((prix - min) / (max - min), 0), 1) : 0.5;
  return (
    <View
      style={styles.range}
      accessible
      accessibilityLabel={`Fourchette de ${formatDh(min)} à ${formatDh(max)}`}
    >
      <View style={styles.rangeTrack}>
        <View style={[styles.rangeMarker, { left: `${position * 100}%` }]} />
      </View>
      <View style={styles.rangeLabels}>
        <Text style={styles.rangeLabel}>{formatDh(min)}</Text>
        <Text style={styles.rangeLabel}>{formatDh(max)}</Text>
      </View>
    </View>
  );
}

export default function EstimateResultScreen({ navigation, route }) {
  const insets = useSafeAreaInsets();
  const { estimation, vehicule } = route.params;
  const fiable = estimation.fiabilite === 'normale';

  const recap = [
    `${displayName(vehicule.marque)} ${displayName(vehicule.modele)}`,
    String(vehicule.annee),
    vehicule.kilometrage ? `${formatThousands(vehicule.kilometrage)} km` : null,
    labelOf(BOITES, vehicule.boite),
    labelOf(CARBURANTS, vehicule.carburant),
    vehicule.etat ? `état ${labelOf(ETATS, vehicule.etat).toLowerCase()}` : null,
  ].filter(Boolean);

  return (
    <ScrollView
      style={styles.flex}
      contentContainerStyle={[styles.content, { paddingBottom: Math.max(insets.bottom, 16) + 8 }]}
    >
      <View style={styles.hero}>
        <Text style={styles.heroLabel}>Valeur estimée</Text>
        <Text style={styles.heroPrice} accessibilityLabel={`Prix estimé ${formatDh(estimation.prix_estime)}`}>
          {formatDh(estimation.prix_estime)}
        </Text>
        <Text style={styles.heroVehicle}>{recap.join(' · ')}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Fourchette de prix</Text>
        <RangeBar min={estimation.fourchette.min} max={estimation.fourchette.max} prix={estimation.prix_estime} />
        <Text style={styles.cardText}>
          8 annonces comparables sur 10 affichent un prix dans cette fourchette.
        </Text>
      </View>

      <View style={[styles.badge, fiable ? styles.badgeOk : styles.badgeWarn]}>
        <Text style={[styles.badgeTitle, fiable ? styles.badgeTitleOk : styles.badgeTitleWarn]}>
          {fiable ? '✓ Estimation fiable' : '⚠ Estimation indicative'}
        </Text>
        {estimation.avertissements.length > 0 ? (
          estimation.avertissements.map((a) => (
            <Text key={a} style={styles.badgeText}>• {a}</Text>
          ))
        ) : (
          <Text style={styles.badgeText}>
            Ce modèle est bien représenté dans les annonces : l'estimation est précise à ~10 % près en moyenne.
          </Text>
        )}
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Comment est calculé ce prix ?</Text>
        <Text style={styles.cardText}>
          Un modèle d'intelligence artificielle a appris les prix de plus de 70 000 annonces de voitures
          d'occasion au Maroc (âge, kilométrage, modèle, boîte, équipements…). Il s'agit d'un prix de
          marché indicatif, au niveau des annonces 2024 : faites toujours inspecter le véhicule avant
          d'acheter ou de vendre.
        </Text>
      </View>

      <View style={styles.actions}>
        <PrimaryButton
          title="Faire inspecter par un garage"
          onPress={() => navigation.getParent()?.navigate('Garages')}
        />
        <PrimaryButton title="Modifier les informations" variant="outline" onPress={() => navigation.goBack()} />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 16 },
  hero: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 24,
    paddingHorizontal: 20,
    alignItems: 'center',
    marginBottom: 12,
  },
  heroLabel: { color: '#D6E4F0', fontSize: 14, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8 },
  heroPrice: { color: '#fff', fontSize: 38, fontWeight: '800', marginTop: 6 },
  heroVehicle: { color: '#D6E4F0', fontSize: 14, marginTop: 8, textAlign: 'center', lineHeight: 20 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  cardTitle: { fontSize: 16, fontWeight: '800', color: colors.text, marginBottom: 12 },
  cardText: { fontSize: 14, color: colors.textMuted, lineHeight: 20 },
  range: { marginBottom: 12 },
  rangeTrack: {
    height: 10,
    borderRadius: 5,
    backgroundColor: '#D6E4F0',
    marginHorizontal: 8,
    justifyContent: 'center',
  },
  rangeMarker: {
    position: 'absolute',
    width: 22,
    height: 22,
    marginLeft: -11,
    borderRadius: 11,
    backgroundColor: colors.accent,
    borderWidth: 3,
    borderColor: '#fff',
  },
  rangeLabels: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 },
  rangeLabel: { fontSize: 14, fontWeight: '700', color: colors.text },
  badge: { borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1 },
  badgeOk: { backgroundColor: '#E9F7EF', borderColor: '#A9DFBF' },
  badgeWarn: { backgroundColor: '#FEF5E7', borderColor: '#F8C471' },
  badgeTitle: { fontSize: 15, fontWeight: '800', marginBottom: 6 },
  badgeTitleOk: { color: colors.success },
  badgeTitleWarn: { color: '#B9770E' },
  badgeText: { fontSize: 14, color: colors.text, lineHeight: 20, marginTop: 2 },
  actions: { gap: 10, marginTop: 4 },
});
