import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, Pressable } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { listMecaniciensEnAttente, validerMecanicien } from '../../api/admin';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

export default function AdminPendingScreen() {
  const [mecaniciens, setMecaniciens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [actionEnCours, setActionEnCours] = useState(null);

  const load = useCallback(async () => {
    try {
      setMecaniciens(await listMecaniciensEnAttente());
      setError('');
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      load().finally(() => setLoading(false));
    }, [load])
  );

  async function handleRefresh() {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }

  async function handleDecision(userId, statut) {
    setActionEnCours(userId);
    try {
      await validerMecanicien(userId, statut);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setActionEnCours(null);
    }
  }

  if (loading) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  return (
    <View style={styles.flex}>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={mecaniciens}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucune revendication en attente</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.nom}</Text>
            <Text style={styles.meta}>{item.telephone}</Text>
            <Text style={styles.meta}>
              Revendique : {item.garage_nom} ({item.garage_ville})
            </Text>
            <View style={styles.actionsRow}>
              <Pressable
                onPress={() => handleDecision(item.id, 'valide')}
                disabled={actionEnCours === item.id}
                style={[styles.actionButton, { backgroundColor: colors.success }]}
              >
                <Text style={styles.actionButtonText}>Valider</Text>
              </Pressable>
              <Pressable
                onPress={() => handleDecision(item.id, 'refuse')}
                disabled={actionEnCours === item.id}
                style={[styles.actionButton, { backgroundColor: colors.danger }]}
              >
                <Text style={styles.actionButtonText}>Refuser</Text>
              </Pressable>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  listContent: { padding: 16 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.text },
  meta: { color: colors.textMuted, marginTop: 4 },
  actionsRow: { flexDirection: 'row', gap: 8, marginTop: 12 },
  actionButton: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8 },
  actionButtonText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', margin: 16 },
});
