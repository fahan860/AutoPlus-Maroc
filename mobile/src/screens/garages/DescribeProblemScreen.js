import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { recommendGarages } from '../../api/garages';
import { extractErrorMessage } from '../../api/client';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

const LONGUEUR_MAX = 500;
const LONGUEUR_MIN = 3;

// Exemples cliquables : montrent le niveau de detail attendu et evitent la page blanche
const EXEMPLES = [
  'Ça grince quand je freine',
  'La clim souffle de l\'air chaud',
  'Voyant moteur allumé',
  'Je dois faire la vidange',
  'Ma portière est enfoncée',
  'La voiture ne démarre pas',
];

const DELAI_POSITION_MS = 8000;
const AGE_MAX_POSITION_CONNUE_MS = 10 * 60 * 1000;

// Position de l'utilisateur, la plus rapide possible : derniere position connue si elle
// est recente, sinon position actuelle (abandon apres 8 s, frequent en interieur).
// Retourne { coords, refusee } : coords null si indisponible, refusee si l'acces est refuse.
async function positionActuelle(positionConnue) {
  if (positionConnue) return { coords: positionConnue, refusee: false };
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return { coords: null, refusee: true };
    const derniere = await Location.getLastKnownPositionAsync({ maxAge: AGE_MAX_POSITION_CONNUE_MS });
    if (derniere) return { coords: derniere.coords, refusee: false };
    const actuelle = await Promise.race([
      Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }),
      new Promise((resolve) => setTimeout(() => resolve(null), DELAI_POSITION_MS)),
    ]);
    return { coords: actuelle?.coords ?? null, refusee: false };
  } catch {
    return { coords: null, refusee: false }; // sans position, le service classe sans la distance
  }
}

// Modele B : l'automobiliste decrit sa panne avec ses mots, l'app trouve le type de
// panne probable et les garages adaptes les plus proches.
export default function DescribeProblemScreen({ navigation, route }) {
  const insets = useSafeAreaInsets();
  const [description, setDescription] = useState(route.params?.description ?? '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const texte = description.trim();
  const valide = texte.length >= LONGUEUR_MIN;

  async function handleSubmit() {
    setError('');
    setLoading(true);
    try {
      const { coords, refusee } = await positionActuelle(route.params?.location);
      const resultat = await recommendGarages({
        description: texte,
        lat: coords?.latitude,
        lon: coords?.longitude,
      });
      navigation.navigate('RecommendedGarages', { resultat, description: texte, positionRefusee: refusee });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Que se passe-t-il avec votre voiture ?</Text>
        <Text style={styles.subtitle}>
          Décrivez le problème avec vos mots : bruit, voyant, odeur, moment où ça arrive…
        </Text>

        <View style={styles.inputCard}>
          <TextInput
            style={styles.input}
            value={description}
            onChangeText={(t) => setDescription(t.slice(0, LONGUEUR_MAX))}
            placeholder="Ex : un bruit de frottement à l'avant quand je freine, depuis hier"
            placeholderTextColor={colors.textMuted}
            multiline
            autoFocus={!route.params?.description}
            textAlignVertical="top"
            accessibilityLabel="Description de la panne"
          />
          <Text style={styles.counter}>{description.length} / {LONGUEUR_MAX}</Text>
        </View>

        <Text style={styles.label}>Exemples</Text>
        <View style={styles.examples}>
          {EXEMPLES.map((exemple) => (
            <Pressable
              key={exemple}
              style={({ pressed }) => [styles.example, pressed && styles.pressed]}
              onPress={() => setDescription(exemple)}
              accessibilityRole="button"
              accessibilityHint="Remplit la description avec cet exemple"
            >
              <Text style={styles.exampleText}>{exemple}</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.info}>
          <Text style={styles.infoText}>
            🔒 Votre description sert uniquement à trouver les garages adaptés. Votre position permet de
            proposer les plus proches.
          </Text>
        </View>

        {error ? <Text style={styles.error}>{error}</Text> : null}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 12) }]}>
        <PrimaryButton
          title={loading ? 'Recherche…' : 'Trouver un garage'}
          onPress={handleSubmit}
          loading={loading}
          disabled={!valide}
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 16, paddingBottom: 24 },
  title: { fontSize: 22, fontWeight: '800', color: colors.text },
  subtitle: { fontSize: 14, color: colors.textMuted, marginTop: 4, marginBottom: 16, lineHeight: 20 },
  inputCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 12,
    marginBottom: 18,
  },
  input: { minHeight: 110, fontSize: 16, color: colors.text, lineHeight: 22 },
  counter: { alignSelf: 'flex-end', fontSize: 12, color: colors.textMuted, marginTop: 4 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8 },
  examples: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 18 },
  example: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    minHeight: 40,
    justifyContent: 'center',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  pressed: { opacity: 0.8 },
  exampleText: { color: colors.text, fontWeight: '600' },
  info: { backgroundColor: '#EAF2F8', borderRadius: 12, padding: 12 },
  infoText: { fontSize: 13, color: colors.primaryDark, lineHeight: 19 },
  error: { color: colors.danger, textAlign: 'center', marginTop: 14 },
  footer: {
    paddingHorizontal: 16,
    paddingTop: 10,
    backgroundColor: colors.surface,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
});
