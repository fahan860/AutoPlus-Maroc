import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, Pressable } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { listVehicles } from '../../api/vehicles';
import { extractErrorMessage } from '../../api/client';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function VehiclesScreen({ navigation }) {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const data = await listVehicles();
      setVehicles(data);
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

  return (
    <View style={styles.flex}>
      <View style={styles.header}>
        <Pressable
          style={({ pressed }) => [styles.promo, pressed && styles.pressed]}
          onPress={() => navigation.navigate('EstimateVehicle')}
          accessibilityRole="button"
          accessibilityLabel="Estimer le prix d'une voiture"
        >
          <Text style={styles.promoIcon}>💰</Text>
          <View style={styles.promoBody}>
            <Text style={styles.promoTitle}>Combien vaut votre voiture ?</Text>
            <Text style={styles.promoText}>Estimation gratuite en 30 secondes</Text>
          </View>
          <Text style={styles.promoChevron}>›</Text>
        </Pressable>
        <PrimaryButton title="Ajouter un vehicule" variant="outline" onPress={() => navigation.navigate('AddVehicle')} />
      </View>

      {loading ? (
        <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />
      ) : error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <FlatList
          data={vehicles}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucun vehicule enregistre pour l'instant</Text>}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.plaque}>{item.plaque}</Text>
              <Text style={styles.meta}>
                {[item.marque, item.modele, item.annee].filter(Boolean).join(' · ') || 'Details non renseignes'}
              </Text>
              <Pressable
                style={styles.estimateLink}
                hitSlop={8}
                onPress={() => navigation.navigate('EstimateVehicle', { vehicle: item })}
                accessibilityRole="button"
                accessibilityLabel={`Estimer la valeur du vehicule ${item.plaque}`}
              >
                <Text style={styles.estimateLinkText}>Estimer sa valeur ›</Text>
              </Pressable>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  header: { padding: 16, gap: 12 },
  promo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    borderRadius: 14,
    padding: 16,
  },
  pressed: { opacity: 0.85 },
  promoIcon: { fontSize: 28, marginRight: 12 },
  promoBody: { flex: 1 },
  promoTitle: { color: '#fff', fontSize: 16, fontWeight: '800' },
  promoText: { color: '#D6E4F0', fontSize: 13, marginTop: 2 },
  promoChevron: { color: '#fff', fontSize: 26, marginLeft: 8 },
  estimateLink: { marginTop: 10, alignSelf: 'flex-start' },
  estimateLinkText: { color: colors.primary, fontWeight: '700' },
  listContent: { paddingHorizontal: 16, paddingBottom: 16 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  plaque: { fontSize: 18, fontWeight: '800', color: colors.text },
  meta: { color: colors.textMuted, marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
