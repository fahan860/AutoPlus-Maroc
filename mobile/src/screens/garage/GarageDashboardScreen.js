import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, Pressable } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getMonGarage } from '../../api/garages';
import { listInterventions, updateInterventionStatut } from '../../api/interventions';
import { extractErrorMessage } from '../../api/client';
import { colors } from '../../theme/colors';

const FILTRES = ['toutes', 'demande', 'confirme', 'en_cours', 'termine'];

const STATUT_LABELS = {
  demande: 'demande',
  confirme: 'confirme',
  en_cours: 'en_cours',
  termine: 'termine',
  annule: 'annule',
};

const STATUT_COLORS = {
  demande: colors.accent,
  confirme: colors.primary,
  en_cours: '#F7C325',
  termine: colors.success,
  annule: colors.danger,
};

// Prochaine action possible selon le statut courant d'une demande de RDV,
// cf. wireframe "5. Dashboard Garagiste" (Accepter/Refuser, Demarrer, Marquer termine).
function actionsPour(statut) {
  if (statut === 'demande') return [{ label: 'Accepter', next: 'confirme', color: colors.success }, { label: 'Refuser', next: 'annule', color: colors.danger }];
  if (statut === 'confirme') return [{ label: 'Demarrer', next: 'en_cours', color: colors.primary }];
  if (statut === 'en_cours') return [{ label: 'Marquer termine', next: 'termine', color: colors.success }];
  return [];
}

export default function GarageDashboardScreen() {
  const [garage, setGarage] = useState(null);
  const [compteurs, setCompteurs] = useState({});
  const [interventions, setInterventions] = useState([]);
  const [filtre, setFiltre] = useState('toutes');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [actionEnCours, setActionEnCours] = useState(null);

  const load = useCallback(async () => {
    try {
      const [monGarage, mesInterventions] = await Promise.all([getMonGarage(), listInterventions()]);
      setGarage(monGarage.garage);
      setCompteurs(monGarage.compteurs_rdv || {});
      setInterventions(mesInterventions);
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

  async function handleAction(interventionId, statut) {
    setActionEnCours(interventionId);
    try {
      await updateInterventionStatut(interventionId, statut);
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

  if (error && !garage) {
    return (
      <View style={styles.flex}>
        <Text style={styles.pendingText}>{error}</Text>
      </View>
    );
  }

  const listeFiltree = filtre === 'toutes' ? interventions : interventions.filter((i) => i.statut === filtre);

  return (
    <View style={styles.flex}>
      <View style={styles.header}>
        <Text style={styles.garageNom}>{garage?.nom}</Text>
        <View style={styles.compteursRow}>
          {['demande', 'confirme', 'en_cours', 'termine'].map((statut) => (
            <View key={statut} style={styles.compteurBox}>
              <Text style={styles.compteurValue}>{compteurs[statut] || 0}</Text>
              <Text style={styles.compteurLabel}>{STATUT_LABELS[statut]}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.filtres}>
        {FILTRES.map((f) => (
          <Pressable key={f} onPress={() => setFiltre(f)} style={[styles.filtreChip, filtre === f && styles.filtreChipActive]}>
            <Text style={[styles.filtreChipText, filtre === f && styles.filtreChipTextActive]}>{f}</Text>
          </Pressable>
        ))}
      </View>

      <FlatList
        data={listeFiltree}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucune demande de rendez-vous</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>{item.type_panne || 'Intervention'}</Text>
              <Text style={[styles.badge, { color: STATUT_COLORS[item.statut] }]}>{STATUT_LABELS[item.statut] || item.statut}</Text>
            </View>
            {item.description ? <Text style={styles.meta}>{item.description}</Text> : null}
            <Text style={styles.date}>
              {item.date_rdv ? new Date(item.date_rdv).toLocaleString('fr-FR') : 'Date non fixee'}
            </Text>

            <View style={styles.actionsRow}>
              {actionsPour(item.statut).map((action) => (
                <Pressable
                  key={action.label}
                  onPress={() => handleAction(item.id, action.next)}
                  disabled={actionEnCours === item.id}
                  style={[styles.actionButton, { backgroundColor: action.color }]}
                >
                  <Text style={styles.actionButtonText}>{action.label}</Text>
                </Pressable>
              ))}
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  header: { padding: 16, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  garageNom: { fontSize: 20, fontWeight: '800', color: colors.text },
  compteursRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 12 },
  compteurBox: { alignItems: 'center', flex: 1 },
  compteurValue: { fontSize: 18, fontWeight: '800', color: colors.primary },
  compteurLabel: { fontSize: 11, color: colors.textMuted, marginTop: 2 },
  filtres: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, padding: 16, paddingBottom: 8 },
  filtreChip: { borderWidth: 1, borderColor: colors.border, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6 },
  filtreChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  filtreChipText: { fontSize: 12, color: colors.text, fontWeight: '600' },
  filtreChipTextActive: { color: '#fff' },
  listContent: { padding: 16, paddingTop: 8 },
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
  actionsRow: { flexDirection: 'row', gap: 8, marginTop: 12 },
  actionButton: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8 },
  actionButtonText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 40, color: colors.textMuted },
  pendingText: { textAlign: 'center', marginTop: 60, padding: 24, color: colors.textMuted, fontSize: 15 },
});
