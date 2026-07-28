import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getMonGarage } from '../../api/garages';
import { listReviews } from '../../api/reviews';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

export default function GarageReviewsScreen() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const { garage } = await getMonGarage();
      setReviews(await listReviews(garage.id));
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
          data={reviews}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucun avis pour l'instant</Text>}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{'⭐'.repeat(Math.round(item.note))} {item.auteur}</Text>
              {item.commentaire ? <Text style={styles.meta}>{item.commentaire}</Text> : null}
              <Text style={styles.date}>{new Date(item.created_at).toLocaleDateString('fr-FR')}</Text>
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
  cardTitle: { fontSize: 15, fontWeight: '700', color: colors.text },
  meta: { color: colors.textMuted, marginTop: 6 },
  date: { color: colors.textMuted, marginTop: 8, fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
