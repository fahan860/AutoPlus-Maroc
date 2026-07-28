import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getMesVehiculesGarage } from '../../api/garages';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

export default function GarageVehiclesScreen() {
  const [vehicules, setVehicules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      setVehicules(await getMesVehiculesGarage());
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
          data={vehicules}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucun vehicule client pour l'instant</Text>}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>
                {item.marque || 'Vehicule'} {item.modele || ''} ({item.plaque})
              </Text>
              <Text style={styles.meta}>Proprietaire : {item.proprietaire}</Text>
              {item.annee ? <Text style={styles.meta}>Annee : {item.annee}</Text> : null}
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
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.text },
  meta: { color: colors.textMuted, marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
