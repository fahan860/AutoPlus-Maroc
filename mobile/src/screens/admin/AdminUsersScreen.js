import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, Pressable } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { listUsers, setUserActif } from '../../api/admin';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

export default function AdminUsersScreen() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [actionEnCours, setActionEnCours] = useState(null);

  const load = useCallback(async () => {
    try {
      setUsers(await listUsers());
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

  async function handleToggleActif(user) {
    setActionEnCours(user.id);
    try {
      await setUserActif(user.id, !user.actif);
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
        data={users}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucun utilisateur</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>{item.nom}</Text>
              <Text style={styles.role}>{item.role}</Text>
            </View>
            <Text style={styles.meta}>{item.telephone}</Text>
            {item.role === 'mecanicien' ? (
              <Text style={styles.meta}>Garage : {item.garage_statut || 'non rattache'}</Text>
            ) : null}
            <Pressable
              onPress={() => handleToggleActif(item)}
              disabled={actionEnCours === item.id}
              style={[styles.actionButton, { backgroundColor: item.actif ? colors.danger : colors.success }]}
            >
              <Text style={styles.actionButtonText}>{item.actif ? 'Desactiver' : 'Activer'}</Text>
            </Pressable>
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
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.text },
  role: { fontSize: 11, color: colors.primary, fontWeight: '700', textTransform: 'uppercase' },
  meta: { color: colors.textMuted, marginTop: 4 },
  actionButton: { alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8, marginTop: 12 },
  actionButtonText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  error: { color: colors.danger, textAlign: 'center', margin: 16 },
});
