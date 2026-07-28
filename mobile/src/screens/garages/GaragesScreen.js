import { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import * as Location from 'expo-location';
import MapView, { Marker } from 'react-native-maps';
import { listGarages } from '../../api/garages';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

const CASABLANCA_REGION = {
  latitude: 33.5731,
  longitude: -7.5898,
  latitudeDelta: 0.15,
  longitudeDelta: 0.15,
};

export default function GaragesScreen({ navigation }) {
  const [viewMode, setViewMode] = useState('liste');
  const [garages, setGarages] = useState([]);
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadGarages = useCallback(async (coords) => {
    try {
      let data = await listGarages(
        coords ? { lat: coords.latitude, lng: coords.longitude, radiusKm: 30 } : {}
      );
      // Peu de garages ont une geoloc exploitable pour l'instant (23/123, voir
      // data/README.md) : si la recherche par proximite ne renvoie rien, on
      // se replie sur la liste complete plutot que de laisser l'ecran vide.
      if (coords && data.length === 0) {
        data = await listGarages({});
      }
      setGarages(data);
      setError('');
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      let coords = null;
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const position = await Location.getCurrentPositionAsync({});
          coords = position.coords;
          setLocation(coords);
        }
      } catch {
        // Position indisponible : on retombe sur la liste triee par note cote API
      }
      await loadGarages(coords);
      setLoading(false);
    })();
  }, [loadGarages]);

  async function handleRefresh() {
    setRefreshing(true);
    await loadGarages(location);
    setRefreshing(false);
  }

  const garagesWithCoords = garages.filter((g) => g.latitude != null && g.longitude != null);

  return (
    <View style={styles.flex}>
      <View style={styles.toggleRow}>
        <ToggleButton label="Liste" active={viewMode === 'liste'} onPress={() => setViewMode('liste')} />
        <ToggleButton label="Carte" active={viewMode === 'carte'} onPress={() => setViewMode('carte')} />
      </View>

      {loading ? (
        <ActivityIndicator style={styles.centered} size="large" color={colors.primary} />
      ) : error ? (
        <Text style={styles.error}>{error}</Text>
      ) : viewMode === 'liste' ? (
        <FlatList
          data={garages}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucun garage trouve</Text>}
          renderItem={({ item }) => (
            <GarageCard garage={item} onPress={() => navigation.navigate('GarageDetail', { garageId: item.id })} />
          )}
        />
      ) : (
        <MapView
          style={styles.flex}
          initialRegion={
            location
              ? { latitude: location.latitude, longitude: location.longitude, latitudeDelta: 0.1, longitudeDelta: 0.1 }
              : CASABLANCA_REGION
          }
        >
          {garagesWithCoords.map((garage) => (
            <Marker
              key={garage.id}
              coordinate={{ latitude: garage.latitude, longitude: garage.longitude }}
              title={garage.nom}
              description={garage.adresse || garage.ville}
              onCalloutPress={() => navigation.navigate('GarageDetail', { garageId: garage.id })}
            />
          ))}
        </MapView>
      )}
    </View>
  );
}

function ToggleButton({ label, active, onPress }) {
  return (
    <Pressable style={[styles.toggleButton, active && styles.toggleButtonActive]} onPress={onPress}>
      <Text style={[styles.toggleText, active && styles.toggleTextActive]}>{label}</Text>
    </Pressable>
  );
}

function GarageCard({ garage, onPress }) {
  return (
    <Pressable style={styles.card} onPress={onPress}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{garage.nom}</Text>
        {garage.note != null && <Text style={styles.cardNote}>★ {garage.note}</Text>}
      </View>
      {garage.categorie ? <Text style={styles.cardMeta}>{garage.categorie}</Text> : null}
      <Text style={styles.cardMeta}>{garage.adresse || garage.ville}</Text>
      {garage.distance_m != null && (
        <Text style={styles.cardDistance}>{(garage.distance_m / 1000).toFixed(1)} km</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  centered: { flex: 1 },
  toggleRow: {
    flexDirection: 'row',
    padding: 12,
    gap: 10,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  toggleButton: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  toggleButtonActive: {
    backgroundColor: colors.primary,
  },
  toggleText: { color: colors.textMuted, fontWeight: '600' },
  toggleTextActive: { color: '#fff' },
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
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.text, flexShrink: 1 },
  cardNote: { color: colors.accent, fontWeight: '700' },
  cardMeta: { color: colors.textMuted, marginTop: 4 },
  cardDistance: { color: colors.primary, fontWeight: '600', marginTop: 6 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
