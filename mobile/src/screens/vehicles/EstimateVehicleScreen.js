import { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  Pressable,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { getEstimateOptions, estimateVehicle } from '../../api/estimate';
import { extractErrorMessage } from '../../api/client';
import ChipGroup from '../../components/ChipGroup';
import SelectField from '../../components/SelectField';
import PrimaryButton from '../../components/PrimaryButton';
import {
  BOITES,
  CARBURANTS,
  ETATS,
  ORIGINES,
  PREMIERE_MAIN,
  EQUIPEMENTS,
  displayName,
  formatThousands,
} from '../../utils/vehicleLabels';
import { colors } from '../../theme/colors';

const ANNEE_MAX = new Date().getFullYear() + 1;
const ANNEE_MIN = 1980;

function normalizeKey(texte) {
  return (texte || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

// Estimation du prix d'un vehicule d'occasion (Modele A).
// Formulaire en deux niveaux : l'essentiel (6 champs) suffit pour estimer ; les details
// facultatifs affinent le resultat sans bloquer l'utilisateur.
export default function EstimateVehicleScreen({ navigation, route }) {
  const insets = useSafeAreaInsets();
  const vehiculeInitial = route.params?.vehicle;

  const [options, setOptions] = useState(null);
  const [optionsError, setOptionsError] = useState('');

  const [marque, setMarque] = useState(normalizeKey(vehiculeInitial?.marque) || null);
  const [modele, setModele] = useState(normalizeKey(vehiculeInitial?.modele) || null);
  const [annee, setAnnee] = useState(vehiculeInitial?.annee ? String(vehiculeInitial.annee) : '');
  const [kilometrage, setKilometrage] = useState('');
  const [boite, setBoite] = useState(null);
  const [carburant, setCarburant] = useState(null);

  const [showDetails, setShowDetails] = useState(false);
  const [puissance, setPuissance] = useState('');
  const [etat, setEtat] = useState(null);
  const [origine, setOrigine] = useState(null);
  const [premiereMain, setPremiereMain] = useState(null);
  const [ville, setVille] = useState(null);
  const [equipements, setEquipements] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function loadOptions() {
    setOptionsError('');
    getEstimateOptions()
      .then(setOptions)
      .catch((err) => setOptionsError(extractErrorMessage(err)));
  }

  useEffect(loadOptions, []);

  const marques = useMemo(() => (options ? options.marques.filter((m) => m !== 'autres') : []), [options]);
  const modeles = useMemo(
    () => (options && marque ? options.modeles_par_marque[marque] || [] : []),
    [options, marque]
  );

  const anneeNum = Number(annee);
  const anneeValide = annee.length === 4 && anneeNum >= ANNEE_MIN && anneeNum <= ANNEE_MAX;

  const manquants = [
    !marque && 'marque',
    !modele && 'modèle',
    !anneeValide && 'année',
    !boite && 'boîte',
    !carburant && 'carburant',
  ].filter(Boolean);

  const nbDetails = [puissance, etat, origine, premiereMain !== null, ville, equipements.length > 0].filter(Boolean).length;

  function handleMarque(nouvelle) {
    setMarque(nouvelle);
    if (nouvelle !== marque) setModele(null); // le modele depend de la marque
  }

  async function handleSubmit() {
    setError('');
    setLoading(true);
    const payload = {
      marque,
      modele,
      annee: anneeNum,
      boite,
      carburant,
      kilometrage: kilometrage ? Number(kilometrage) : undefined,
      puissance_fiscale: puissance ? Number(puissance) : undefined,
      etat: etat || undefined,
      origine: origine || undefined,
      premiere_main: premiereMain ?? undefined,
      ville: ville || undefined,
      equipements,
    };
    try {
      const estimation = await estimateVehicle(payload);
      navigation.navigate('EstimateResult', { estimation, vehicule: payload });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (!options) {
    return (
      <View style={[styles.flex, styles.centered]}>
        {optionsError ? (
          <>
            <Text style={styles.errorTitle}>Service d'estimation indisponible</Text>
            <Text style={styles.errorText}>{optionsError}</Text>
            <View style={styles.retry}>
              <PrimaryButton title="Réessayer" variant="outline" onPress={loadOptions} />
            </View>
          </>
        ) : (
          <ActivityIndicator size="large" color={colors.primary} />
        )}
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.intro}>
          <Text style={styles.introTitle}>Combien vaut votre voiture ?</Text>
          <Text style={styles.introText}>
            Estimation basée sur plus de 70 000 annonces de voitures d'occasion au Maroc.
          </Text>
        </View>

        {/* --- L'essentiel --- */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Le véhicule</Text>
          <SelectField
            label="Marque"
            value={marque}
            options={marques}
            onChange={handleMarque}
            getLabel={displayName}
            placeholder="Ex : Dacia"
            searchPlaceholder="Rechercher une marque"
            allowCustom
          />
          <SelectField
            label="Modèle"
            value={modele}
            options={modeles}
            onChange={setModele}
            getLabel={displayName}
            placeholder="Ex : Logan"
            searchPlaceholder="Rechercher un modèle"
            disabled={!marque}
            disabledHint="Choisissez d'abord la marque"
            allowCustom
          />
          <View style={styles.row}>
            <View style={styles.rowItem}>
              <Text style={styles.label}>Année</Text>
              <TextInput
                style={[styles.input, annee.length === 4 && !anneeValide && styles.inputError]}
                value={annee}
                onChangeText={(t) => setAnnee(t.replace(/\D/g, '').slice(0, 4))}
                placeholder="2019"
                placeholderTextColor={colors.textMuted}
                keyboardType="number-pad"
                maxLength={4}
                accessibilityLabel="Année de mise en circulation"
              />
            </View>
            <View style={styles.rowItem}>
              <Text style={styles.label}>Kilométrage</Text>
              <View style={styles.inputWithSuffix}>
                <TextInput
                  style={styles.inputFlex}
                  value={kilometrage ? formatThousands(kilometrage) : ''}
                  onChangeText={(t) => setKilometrage(t.replace(/\D/g, '').slice(0, 7))}
                  placeholder="90 000"
                  placeholderTextColor={colors.textMuted}
                  keyboardType="number-pad"
                  accessibilityLabel="Kilométrage en kilomètres"
                />
                <Text style={styles.suffix}>km</Text>
              </View>
            </View>
          </View>
          {annee.length === 4 && !anneeValide ? (
            <Text style={styles.fieldError}>L'année doit être comprise entre {ANNEE_MIN} et {ANNEE_MAX}</Text>
          ) : null}

          <Text style={styles.label}>Boîte de vitesses</Text>
          <ChipGroup options={BOITES} value={boite} onChange={setBoite} />
          <Text style={[styles.label, styles.spaced]}>Carburant</Text>
          <ChipGroup options={CARBURANTS} value={carburant} onChange={setCarburant} />
        </View>

        {/* --- Details facultatifs --- */}
        <Pressable
          style={({ pressed }) => [styles.detailsToggle, pressed && styles.pressed]}
          onPress={() => setShowDetails((v) => !v)}
          accessibilityRole="button"
          accessibilityState={{ expanded: showDetails }}
        >
          <View style={styles.flexShrink}>
            <Text style={styles.detailsTitle}>Affiner l'estimation</Text>
            <Text style={styles.detailsSubtitle}>
              {nbDetails > 0 ? `${nbDetails} détail${nbDetails > 1 ? 's' : ''} ajouté${nbDetails > 1 ? 's' : ''}` : 'État, origine, ville, équipements… (facultatif)'}
            </Text>
          </View>
          <Text style={styles.detailsChevron}>{showDetails ? '−' : '+'}</Text>
        </Pressable>

        {showDetails ? (
          <View style={styles.card}>
            <Text style={styles.label}>État général</Text>
            <ChipGroup options={ETATS} value={etat} onChange={setEtat} allowDeselect />

            <Text style={[styles.label, styles.spaced]}>Origine</Text>
            <ChipGroup options={ORIGINES} value={origine} onChange={setOrigine} allowDeselect />

            <Text style={[styles.label, styles.spaced]}>Première main</Text>
            <ChipGroup options={PREMIERE_MAIN} value={premiereMain} onChange={setPremiereMain} allowDeselect />

            <View style={[styles.row, styles.spaced]}>
              <View style={styles.rowItem}>
                <Text style={styles.label}>Puissance fiscale</Text>
                <View style={styles.inputWithSuffix}>
                  <TextInput
                    style={styles.inputFlex}
                    value={puissance}
                    onChangeText={(t) => setPuissance(t.replace(/\D/g, '').slice(0, 2))}
                    placeholder="6"
                    placeholderTextColor={colors.textMuted}
                    keyboardType="number-pad"
                    accessibilityLabel="Puissance fiscale en chevaux"
                  />
                  <Text style={styles.suffix}>CV</Text>
                </View>
              </View>
              <View style={styles.rowItem} />
            </View>

            <SelectField
              label="Ville"
              value={ville}
              options={options.villes}
              onChange={setVille}
              placeholder="Ex : Casablanca"
              searchPlaceholder="Rechercher une ville"
              optional
            />

            <Text style={styles.label}>Équipements</Text>
            <ChipGroup options={EQUIPEMENTS} values={equipements} onChange={setEquipements} multiple />
          </View>
        ) : null}

        {error ? <Text style={styles.submitError}>{error}</Text> : null}
      </ScrollView>

      {/* Bouton toujours visible : l'utilisateur sait a tout moment ce qu'il manque */}
      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 12) }]}>
        {manquants.length > 0 ? (
          <Text style={styles.missing}>À compléter : {manquants.join(', ')}</Text>
        ) : !kilometrage ? (
          <Text style={styles.missing}>Conseil : indiquez le kilométrage pour plus de précision</Text>
        ) : null}
        <PrimaryButton
          title="Estimer le prix"
          onPress={handleSubmit}
          loading={loading}
          disabled={manquants.length > 0}
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  flexShrink: { flexShrink: 1 },
  centered: { alignItems: 'center', justifyContent: 'center', padding: 24 },
  content: { padding: 16, paddingBottom: 24 },
  intro: { marginBottom: 16, paddingHorizontal: 4 },
  introTitle: { fontSize: 22, fontWeight: '800', color: colors.text },
  introText: { fontSize: 14, color: colors.textMuted, marginTop: 4, lineHeight: 20 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  cardTitle: { fontSize: 16, fontWeight: '800', color: colors.text, marginBottom: 14 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8 },
  spaced: { marginTop: 16 },
  row: { flexDirection: 'row', gap: 12 },
  rowItem: { flex: 1 },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    minHeight: 48,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
    marginBottom: 14,
  },
  inputError: { borderColor: colors.danger },
  inputWithSuffix: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    minHeight: 48,
    backgroundColor: colors.surface,
    marginBottom: 14,
  },
  inputFlex: { flex: 1, fontSize: 16, color: colors.text, paddingVertical: 10 },
  suffix: { fontSize: 15, color: colors.textMuted, marginLeft: 6 },
  fieldError: { color: colors.danger, fontSize: 13, marginTop: -8, marginBottom: 12 },
  detailsToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    borderStyle: 'dashed',
    marginBottom: 12,
  },
  pressed: { opacity: 0.8 },
  detailsTitle: { fontSize: 16, fontWeight: '700', color: colors.primary },
  detailsSubtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  detailsChevron: { fontSize: 24, fontWeight: '600', color: colors.primary, marginLeft: 12 },
  submitError: { color: colors.danger, textAlign: 'center', marginTop: 4 },
  footer: {
    paddingHorizontal: 16,
    paddingTop: 10,
    backgroundColor: colors.surface,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  missing: { fontSize: 13, color: colors.textMuted, textAlign: 'center', marginBottom: 8 },
  errorTitle: { fontSize: 18, fontWeight: '800', color: colors.text, textAlign: 'center' },
  errorText: { color: colors.textMuted, textAlign: 'center', marginTop: 6 },
  retry: { marginTop: 18, alignSelf: 'stretch' },
});
