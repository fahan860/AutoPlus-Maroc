import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Linking,
} from 'react-native';
import * as Location from 'expo-location';
import { sendAgentMessage } from '../../api/agent';
import { listVehicles } from '../../api/vehicles';
import { extractErrorMessage } from '../../api/client';
import { URGENCES } from '../../utils/pannes';
import { colors } from '../../theme/colors';

const LONGUEUR_MAX = 1000;
const EXEMPLES = [
  'Ça grince quand je freine',
  'Voyant moteur allumé',
  'La voiture ne démarre pas le matin',
  'tomobil dyali katsfer mli kanfrani',
];

// Position pour classer les garages par distance : derniere position connue, sans attendre
async function positionRapide() {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return null;
    const derniere = await Location.getLastKnownPositionAsync({ maxAge: 30 * 60 * 1000 });
    return derniere?.coords ?? null;
  } catch {
    return null;
  }
}

function Bulle({ message }) {
  const utilisateur = message.role === 'user';
  return (
    <View style={[styles.bulle, utilisateur ? styles.bulleUser : styles.bulleAssistant]}>
      <Text style={[styles.bulleTexte, utilisateur && styles.bulleTexteUser]}>{message.content}</Text>
    </View>
  );
}

function Analyse({ reponse, onGarage }) {
  const urgence = reponse.gravite ? URGENCES[reponse.gravite] : null;
  const darija = reponse.langue === 'darija';
  return (
    <View style={styles.analyse}>
      {reponse.alerte_securite ? (
        <View style={styles.alerte} accessibilityRole="alert">
          <Text style={styles.alerteTitre}>⚠ Arrêtez-vous dès que possible en sécurité</Text>
          <Text style={styles.alerteTexte}>Wqef f blasa mamna, ma tkemmelch tsog.</Text>
        </View>
      ) : null}

      {urgence ? (
        <View style={[styles.badge, { backgroundColor: urgence.fond }]}>
          <Text style={[styles.badgeTexte, { color: urgence.couleur }]}>{urgence.label}</Text>
        </View>
      ) : null}

      {reponse.causes.length > 0 ? (
        <View style={styles.bloc}>
          <Text style={styles.blocTitre}>{darija ? 'Chno ymken ykoun' : 'Causes possibles'}</Text>
          {reponse.causes.map((c) => (
            <View key={c.source + c.titre} style={styles.cause}>
              <Text style={styles.causeTitre}>• {c.titre}</Text>
              {c.explication ? <Text style={styles.causeTexte}>{c.explication}</Text> : null}
            </View>
          ))}
        </View>
      ) : null}

      {reponse.verifications.length > 0 ? (
        <View style={styles.bloc}>
          <Text style={styles.blocTitre}>{darija ? 'Chno tqder tchouf' : 'À vérifier, sans risque'}</Text>
          {reponse.verifications.map((v) => (
            <Text key={v} style={styles.verification}>✓ {v}</Text>
          ))}
        </View>
      ) : null}

      {reponse.garages.length > 0 ? (
        <View style={styles.bloc}>
          <Text style={styles.blocTitre}>{darija ? 'Garages qrab lik' : 'Garages conseillés'}</Text>
          {reponse.garages.map((g) => (
            <View key={g.id} style={styles.garage}>
              <Pressable onPress={() => onGarage(g.id)} accessibilityRole="button" style={styles.garageInfos}>
                <Text style={styles.garageNom}>{g.nom}</Text>
                <Text style={styles.garageRaisons}>{g.raisons.join(' · ')}</Text>
              </Pressable>
              {g.telephone ? (
                <Pressable
                  onPress={() => Linking.openURL(`tel:${g.telephone.replace(/\s/g, '')}`)}
                  accessibilityRole="button"
                  accessibilityLabel={`Appeler ${g.nom}`}
                  hitSlop={8}
                  style={styles.garageAppel}
                >
                  <Text style={styles.garageAppelTexte}>📞</Text>
                </Pressable>
              ) : null}
            </View>
          ))}
        </View>
      ) : null}

      {reponse.sources.length > 0 ? (
        <Text style={styles.sources}>Sources : {reponse.sources.map((s) => s.titre).join(' ; ')}</Text>
      ) : null}
      <Text style={styles.avertissement}>
        Analyse indicative, pas un diagnostic : faites toujours vérifier par un garage.
      </Text>
    </View>
  );
}

// Assistant IA de diagnostic : conversation libre (francais ou darija), questions de precision,
// analyse prudente avec sources, puis garages conseilles (Modele B).
export default function AssistantScreen({ navigation }) {
  const [messages, setMessages] = useState([]); // { role, content, action?, reponse? }
  const [texte, setTexte] = useState('');
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState('');
  const [vehicules, setVehicules] = useState([]);
  const [vehiculeId, setVehiculeId] = useState(null);
  const position = useRef(null);
  const defilement = useRef(null);

  useEffect(() => {
    listVehicles().then(setVehicules).catch(() => {});
    positionRapide().then((coords) => {
      position.current = coords;
    });
  }, []);

  function nouvelleConversation() {
    setMessages([]);
    setErreur('');
    setTexte('');
  }

  // A gauche : a droite, le bouton etait cache par celui de developpement d'Expo Go sur iPhone
  useLayoutEffect(() => {
    navigation.setOptions({
      headerLeft: () =>
        messages.length > 0 ? (
          <Pressable onPress={nouvelleConversation} hitSlop={10} style={styles.headerBouton} accessibilityRole="button">
            <Text style={styles.headerBoutonTexte}>Nouvelle</Text>
          </Pressable>
        ) : null,
    });
  }, [navigation, messages.length]);

  // base : l'historique auquel ajouter le message (sans le dernier message en echec pour Reessayer)
  async function envoyer(contenu, base = messages) {
    const propre = (contenu ?? texte).trim();
    if (!propre || chargement) return;
    const historique = [...base, { role: 'user', content: propre }];
    setMessages(historique);
    setTexte('');
    setErreur('');
    setChargement(true);
    const vehicule = vehicules.find((v) => v.id === vehiculeId);
    try {
      const reponse = await sendAgentMessage({
        messages: historique,
        vehicule: vehicule ? { marque: vehicule.marque, modele: vehicule.modele, annee: vehicule.annee } : null,
        lat: position.current?.latitude,
        lon: position.current?.longitude,
      });
      setMessages([...historique, { role: 'assistant', content: reponse.message, action: reponse.action, reponse }]);
    } catch (err) {
      setErreur(extractErrorMessage(err));
    } finally {
      setChargement(false);
    }
  }

  function reessayer() {
    const dernier = messages[messages.length - 1];
    if (dernier?.role !== 'user') return;
    envoyer(dernier.content, messages.slice(0, -1));
  }

  const dernier = messages[messages.length - 1];
  const suggestions = !chargement && dernier?.role === 'assistant' ? dernier.reponse?.suggestions ?? [] : [];

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <ScrollView
        ref={defilement}
        style={styles.flex}
        contentContainerStyle={styles.contenu}
        keyboardShouldPersistTaps="handled"
        onContentSizeChange={() => defilement.current?.scrollToEnd({ animated: true })}
      >
        {messages.length === 0 ? (
          <View style={styles.accueil}>
            <Text style={styles.accueilIcone}>🤖</Text>
            <Text style={styles.accueilTitre}>Décrivez le problème de votre voiture</Text>
            <Text style={styles.accueilTexte}>
              En français ou en darija. L'assistant pose des questions si besoin, puis propose des pistes et des
              garages adaptés.
            </Text>

            {vehicules.length > 0 ? (
              <>
                <Text style={styles.label}>Votre véhicule (facultatif)</Text>
                <View style={styles.puces}>
                  {vehicules.map((v) => {
                    const actif = v.id === vehiculeId;
                    return (
                      <Pressable
                        key={v.id}
                        onPress={() => setVehiculeId(actif ? null : v.id)}
                        accessibilityRole="radio"
                        accessibilityState={{ selected: actif }}
                        style={[styles.puce, actif && styles.puceActive]}
                      >
                        <Text style={[styles.puceTexte, actif && styles.puceTexteActive]}>
                          {[v.marque, v.modele, v.annee].filter(Boolean).join(' ') || v.plaque}
                        </Text>
                      </Pressable>
                    );
                  })}
                </View>
              </>
            ) : null}

            <Text style={styles.label}>Exemples</Text>
            <View style={styles.puces}>
              {EXEMPLES.map((e) => (
                <Pressable key={e} onPress={() => envoyer(e)} style={styles.puce} accessibilityRole="button">
                  <Text style={styles.puceTexte}>{e}</Text>
                </Pressable>
              ))}
            </View>
          </View>
        ) : null}

        {messages.map((m, i) => (
          <View key={i}>
            <Bulle message={m} />
            {m.reponse?.action === 'diagnostic' ? (
              <>
                <Analyse
                  reponse={m.reponse}
                  onGarage={(garageId) => navigation.navigate('Garages', { screen: 'GarageDetail', params: { garageId } })}
                />
                {i === messages.length - 1 ? (
                  // Un autre probleme = une nouvelle conversation : sinon l'agent melange les symptomes
                  <Pressable onPress={nouvelleConversation} style={styles.nouveau} accessibilityRole="button">
                    <Text style={styles.nouveauTexte}>+ Décrire un autre problème</Text>
                  </Pressable>
                ) : null}
              </>
            ) : null}
          </View>
        ))}

        {chargement ? (
          <View style={[styles.bulle, styles.bulleAssistant, styles.reflexion]}>
            <ActivityIndicator size="small" color={colors.primary} />
            <Text style={styles.reflexionTexte}>L'assistant réfléchit…</Text>
          </View>
        ) : null}

        {erreur ? (
          <View style={styles.erreur}>
            <Text style={styles.erreurTexte}>{erreur}</Text>
            <Pressable onPress={reessayer} accessibilityRole="button" hitSlop={8}>
              <Text style={styles.erreurAction}>Réessayer</Text>
            </Pressable>
          </View>
        ) : null}
      </ScrollView>

      {suggestions.length > 0 ? (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.suggestions}
          contentContainerStyle={styles.suggestionsContenu} keyboardShouldPersistTaps="handled">
          {suggestions.map((s) => (
            <Pressable key={s} onPress={() => envoyer(s)} style={styles.suggestion} accessibilityRole="button">
              <Text style={styles.suggestionTexte}>{s}</Text>
            </Pressable>
          ))}
        </ScrollView>
      ) : null}

      <View style={styles.saisie}>
        <TextInput
          style={styles.champ}
          value={texte}
          onChangeText={(t) => setTexte(t.slice(0, LONGUEUR_MAX))}
          placeholder="Votre message…"
          placeholderTextColor={colors.textMuted}
          multiline
          editable={!chargement}
          accessibilityLabel="Message pour l'assistant"
        />
        <Pressable
          onPress={() => envoyer()}
          disabled={!texte.trim() || chargement}
          accessibilityRole="button"
          accessibilityLabel="Envoyer"
          style={({ pressed }) => [styles.envoyer, (!texte.trim() || chargement) && styles.envoyerInactif, pressed && styles.presse]}
        >
          <Text style={styles.envoyerTexte}>↑</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  contenu: { padding: 16, paddingBottom: 24 },
  presse: { opacity: 0.8 },
  headerBouton: { paddingHorizontal: 12 },
  headerBoutonTexte: { color: colors.primary, fontWeight: '700', fontSize: 15 },
  accueil: { alignItems: 'stretch', marginTop: 8 },
  accueilIcone: { fontSize: 40, textAlign: 'center' },
  accueilTitre: { fontSize: 20, fontWeight: '800', color: colors.text, textAlign: 'center', marginTop: 8 },
  accueilTexte: { fontSize: 14, color: colors.textMuted, textAlign: 'center', marginTop: 6, lineHeight: 20, marginBottom: 18 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8 },
  puces: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 18 },
  puce: {
    paddingHorizontal: 14, paddingVertical: 9, minHeight: 40, justifyContent: 'center',
    borderRadius: 20, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface,
  },
  puceActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  puceTexte: { color: colors.text, fontWeight: '600' },
  puceTexteActive: { color: '#fff' },
  bulle: { maxWidth: '85%', borderRadius: 16, paddingHorizontal: 14, paddingVertical: 10, marginBottom: 10 },
  bulleUser: { alignSelf: 'flex-end', backgroundColor: colors.primary, borderBottomRightRadius: 4 },
  bulleAssistant: {
    alignSelf: 'flex-start', backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderBottomLeftRadius: 4,
  },
  bulleTexte: { fontSize: 15, color: colors.text, lineHeight: 21 },
  bulleTexteUser: { color: '#fff' },
  reflexion: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  reflexionTexte: { color: colors.textMuted, fontStyle: 'italic' },
  nouveau: {
    alignSelf: 'center', paddingHorizontal: 18, paddingVertical: 10, borderRadius: 20, borderWidth: 1.5,
    borderColor: colors.primary, marginBottom: 14,
  },
  nouveauTexte: { color: colors.primary, fontWeight: '700' },
  analyse: {
    backgroundColor: colors.surface, borderRadius: 14, borderWidth: 1, borderColor: colors.border,
    padding: 14, marginBottom: 14, gap: 12,
  },
  alerte: { backgroundColor: colors.danger, borderRadius: 10, padding: 12 },
  alerteTitre: { color: '#fff', fontWeight: '800', fontSize: 15 },
  alerteTexte: { color: '#fff', marginTop: 4 },
  badge: { alignSelf: 'flex-start', borderRadius: 12, paddingHorizontal: 10, paddingVertical: 5 },
  badgeTexte: { fontWeight: '700', fontSize: 13 },
  bloc: { gap: 6 },
  blocTitre: { fontSize: 14, fontWeight: '800', color: colors.text },
  cause: { gap: 2 },
  causeTitre: { fontSize: 14, fontWeight: '600', color: colors.text },
  causeTexte: { fontSize: 13, color: colors.textMuted, lineHeight: 19, marginLeft: 12 },
  verification: { fontSize: 14, color: colors.text, lineHeight: 20 },
  garage: {
    flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    padding: 10,
  },
  garageInfos: { flex: 1 },
  garageNom: { fontSize: 14, fontWeight: '700', color: colors.primary },
  garageRaisons: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  garageAppel: { paddingHorizontal: 8, minHeight: 40, justifyContent: 'center' },
  garageAppelTexte: { fontSize: 20 },
  sources: { fontSize: 12, color: colors.textMuted, fontStyle: 'italic' },
  avertissement: { fontSize: 12, color: colors.textMuted },
  erreur: { backgroundColor: '#FDEDEC', borderRadius: 12, padding: 12, marginBottom: 10 },
  erreurTexte: { color: colors.danger },
  erreurAction: { color: colors.primary, fontWeight: '700', marginTop: 6 },
  suggestions: { flexGrow: 0, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border },
  suggestionsContenu: { padding: 10, gap: 8 },
  suggestion: {
    paddingHorizontal: 14, paddingVertical: 9, borderRadius: 18, borderWidth: 1.5, borderColor: colors.primary,
    backgroundColor: colors.surface,
  },
  suggestionTexte: { color: colors.primary, fontWeight: '700' },
  saisie: {
    flexDirection: 'row', alignItems: 'flex-end', gap: 8, padding: 10, backgroundColor: colors.surface,
    borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border,
  },
  champ: {
    flex: 1, minHeight: 44, maxHeight: 120, borderWidth: 1, borderColor: colors.border, borderRadius: 22,
    paddingHorizontal: 16, paddingTop: 11, paddingBottom: 11, fontSize: 15, color: colors.text,
    backgroundColor: colors.background,
  },
  envoyer: {
    width: 44, height: 44, borderRadius: 22, backgroundColor: colors.primary, alignItems: 'center',
    justifyContent: 'center',
  },
  envoyerInactif: { opacity: 0.4 },
  envoyerTexte: { color: '#fff', fontSize: 22, fontWeight: '800' },
});
