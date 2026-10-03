import { useCallback, useState } from 'react';
import { View, Text, FlatList, Pressable, StyleSheet, ActivityIndicator, RefreshControl, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { listConversations, deleteConversation } from '../../api/agent';
import { extractErrorMessage } from '../../api/client';
import { URGENCES } from '../../utils/pannes';
import { colors } from '../../theme/colors';

// "il y a 2 h", "hier", "12 sept." : lisible d'un coup d'oeil dans une liste
function dateCourte(iso) {
  const date = new Date(iso);
  const minutes = Math.round((Date.now() - date.getTime()) / 60000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  if (minutes < 24 * 60) return `il y a ${Math.round(minutes / 60)} h`;
  if (minutes < 48 * 60) return 'hier';
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

// Historique des conversations avec l'assistant : rouvrir pour relire ou continuer, supprimer.
export default function ConversationsScreen({ navigation }) {
  const [conversations, setConversations] = useState([]);
  const [chargement, setChargement] = useState(true);
  const [rafraichissement, setRafraichissement] = useState(false);
  const [erreur, setErreur] = useState('');

  const charger = useCallback(async () => {
    try {
      setConversations(await listConversations());
      setErreur('');
    } catch (err) {
      setErreur(extractErrorMessage(err));
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      charger().finally(() => setChargement(false));
    }, [charger])
  );

  function supprimer(conversation) {
    Alert.alert('Supprimer cette conversation ?', conversation.titre, [
      { text: 'Annuler', style: 'cancel' },
      {
        text: 'Supprimer',
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteConversation(conversation.id);
            setConversations((liste) => liste.filter((c) => c.id !== conversation.id));
          } catch (err) {
            Alert.alert('Suppression impossible', extractErrorMessage(err));
          }
        },
      },
    ]);
  }

  if (chargement) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  return (
    <FlatList
      style={styles.flex}
      contentContainerStyle={styles.contenu}
      data={conversations}
      keyExtractor={(c) => String(c.id)}
      refreshControl={
        <RefreshControl
          refreshing={rafraichissement}
          onRefresh={async () => {
            setRafraichissement(true);
            await charger();
            setRafraichissement(false);
          }}
        />
      }
      ListHeaderComponent={erreur ? <Text style={styles.erreur}>{erreur}</Text> : null}
      ListEmptyComponent={
        <View style={styles.vide}>
          <Text style={styles.videIcone}>💬</Text>
          <Text style={styles.videTitre}>Aucune conversation pour l'instant</Text>
          <Text style={styles.videTexte}>Vos échanges avec l'assistant apparaîtront ici.</Text>
        </View>
      }
      renderItem={({ item }) => {
        const urgence = item.derniere_gravite ? URGENCES[item.derniere_gravite] : null;
        return (
          <Pressable
            style={({ pressed }) => [styles.carte, pressed && styles.presse]}
            onPress={() => navigation.navigate('AssistantChat', { conversationId: item.id })}
            accessibilityRole="button"
            accessibilityHint="Rouvre la conversation"
          >
            <View style={styles.carteCorps}>
              <Text style={styles.titre} numberOfLines={2}>{item.titre}</Text>
              <View style={styles.meta}>
                <Text style={styles.date}>{dateCourte(item.updated_at)}</Text>
                {urgence ? (
                  <View style={[styles.badge, { backgroundColor: urgence.fond }]}>
                    <Text style={[styles.badgeTexte, { color: urgence.couleur }]}>{urgence.label}</Text>
                  </View>
                ) : null}
              </View>
            </View>
            <Pressable
              onPress={() => supprimer(item)}
              hitSlop={10}
              style={styles.supprimer}
              accessibilityRole="button"
              accessibilityLabel={`Supprimer la conversation ${item.titre}`}
            >
              <Text style={styles.supprimerTexte}>🗑</Text>
            </Pressable>
          </Pressable>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  contenu: { padding: 16, flexGrow: 1 },
  presse: { opacity: 0.85 },
  carte: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, borderRadius: 12,
    borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 10,
  },
  carteCorps: { flex: 1 },
  titre: { fontSize: 15, fontWeight: '700', color: colors.text },
  meta: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 6, flexWrap: 'wrap' },
  date: { fontSize: 13, color: colors.textMuted },
  badge: { borderRadius: 10, paddingHorizontal: 8, paddingVertical: 3 },
  badgeTexte: { fontSize: 12, fontWeight: '700' },
  supprimer: { paddingHorizontal: 8, minHeight: 44, justifyContent: 'center' },
  supprimerTexte: { fontSize: 20 },
  vide: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60 },
  videIcone: { fontSize: 40 },
  videTitre: { fontSize: 17, fontWeight: '800', color: colors.text, marginTop: 10 },
  videTexte: { fontSize: 14, color: colors.textMuted, marginTop: 4 },
  erreur: { color: colors.danger, marginBottom: 12, textAlign: 'center' },
});
