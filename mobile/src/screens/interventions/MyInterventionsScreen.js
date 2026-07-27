import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { listInterventions } from '../../api/interventions';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

const STATUT_LABELS = {
  demande: 'Demande envoyee',
  confirme: 'Confirme',
  en_cours: 'En cours',
  termine: 'Termine',
  annule: 'Annule',
};

const STATUT_COLORS = {
  demande: colors.textMuted,
  confirme: colors.primary,
  en_cours: colors.accent,
  termine: colors.success,
  annule: colors.danger,
};

export default function MyInterventionsScreen() {
  const [interventions, setInterventions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const data = await listInterventions();
      setInterventions(data);
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

  if (loading) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  return (
    <View style={styles.flex}>
      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <FlatList
          data={interventions}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucune demande de rendez-vous pour l'instant</Text>}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.type_panne || 'Intervention'}</Text>
                <Text style={[styles.badge, { color: STATUT_COLORS[item.statut] }]}>
                  {STATUT_LABELS[item.statut] || item.statut}
                </Text>
              </View>
              {item.description ? <Text style={styles.meta}>{item.description}</Text> : null}
              <Text style={styles.date}>
                Cree le {new Date(item.created_at).toLocaleDateString('fr-FR')}
              </Text>
            </View>
          )}
        />
      )}
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
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.text },
  badge: { fontWeight: '700', fontSize: 12, textTransform: 'uppercase' },
  meta: { color: colors.textMuted, marginTop: 6 },
  date: { color: colors.textMuted, marginTop: 8, fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
