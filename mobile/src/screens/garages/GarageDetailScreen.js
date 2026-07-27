import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Linking } from 'react-native';
import { getGarage } from '../../api/garages';
import { extractErrorMessage } from '../../api/client';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function GarageDetailScreen({ route, navigation }) {
  const { garageId } = route.params;
  const [garage, setGarage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getGarage(garageId)
      .then(setGarage)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [garageId]);

  if (loading) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  if (error || !garage) {
    return <Text style={styles.error}>{error || 'Garage introuvable'}</Text>;
  }

  return (
    <ScrollView style={styles.flex} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{garage.nom}</Text>
      {garage.categorie ? <Text style={styles.tag}>{garage.categorie}</Text> : null}

      <View style={styles.section}>
        <InfoRow label="Adresse" value={garage.adresse || 'Non renseignee'} />
        <InfoRow label="Ville" value={garage.ville} />
        <InfoRow label="Telephone" value={garage.telephone || 'Non renseigne'} />
        <InfoRow label="Note" value={garage.note != null ? `★ ${garage.note} (${garage.nb_avis} avis)` : 'Pas encore note'} />
      </View>

      {garage.telephone ? (
        <PrimaryButton
          title="Appeler le garage"
          variant="outline"
          onPress={() => Linking.openURL(`tel:${garage.telephone}`)}
        />
      ) : null}

      <View style={styles.spacer} />

      <PrimaryButton
        title="Prendre rendez-vous"
        onPress={() => navigation.navigate('BookIntervention', { garageId: garage.id, garageNom: garage.nom })}
      />
    </ScrollView>
  );
}

function InfoRow({ label, value }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text },
  tag: { color: colors.primary, fontWeight: '600', marginTop: 4 },
  section: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginVertical: 20,
  },
  infoRow: { marginBottom: 12 },
  infoLabel: { fontSize: 12, color: colors.textMuted, fontWeight: '600', textTransform: 'uppercase' },
  infoValue: { fontSize: 16, color: colors.text, marginTop: 2 },
  spacer: { height: 12 },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
});
