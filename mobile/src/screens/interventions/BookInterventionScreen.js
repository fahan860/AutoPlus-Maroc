import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { listVehicles } from '../../api/vehicles';
import { createIntervention } from '../../api/interventions';
import { extractErrorMessage } from '../../api/client';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

const TYPES_PANNE = ['Vidange', 'Freins', 'Climatisation', 'Diagnostic', 'Pneus', 'Autre'];

export default function BookInterventionScreen({ route, navigation }) {
  const { garageId, garageNom } = route.params;
  const [vehicles, setVehicles] = useState([]);
  const [loadingVehicles, setLoadingVehicles] = useState(true);
  const [selectedVehicleId, setSelectedVehicleId] = useState(null);
  const [typePanne, setTypePanne] = useState(TYPES_PANNE[0]);
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    listVehicles()
      .then((data) => {
        setVehicles(data);
        if (data[0]) setSelectedVehicleId(data[0].id);
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoadingVehicles(false));
  }, []);

  async function handleSubmit() {
    setError('');
    if (!selectedVehicleId) {
      setError('Selectionnez un vehicule');
      return;
    }
    setSubmitting(true);
    try {
      await createIntervention({ vehicleId: selectedVehicleId, garageId, typePanne, description });
      setSuccess(true);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (loadingVehicles) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  if (success) {
    return (
      <View style={[styles.flex, styles.centeredContent]}>
        <Text style={styles.successTitle}>Demande envoyee !</Text>
        <Text style={styles.successText}>Le garage {garageNom} va confirmer votre rendez-vous.</Text>
        <PrimaryButton title="Voir mes RDV" onPress={() => navigation.navigate('Mes RDV')} />
      </View>
    );
  }

  if (vehicles.length === 0) {
    return (
      <View style={[styles.flex, styles.centeredContent]}>
        <Text style={styles.successText}>
          Vous devez d'abord ajouter un vehicule avant de prendre rendez-vous.
        </Text>
        <PrimaryButton
          title="Ajouter un vehicule"
          onPress={() => navigation.navigate('Vehicules', { screen: 'AddVehicle' })}
        />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Rendez-vous chez {garageNom}</Text>

        <Text style={styles.label}>Vehicule</Text>
        <View style={styles.chipRow}>
          {vehicles.map((vehicle) => (
            <Chip
              key={vehicle.id}
              label={vehicle.plaque}
              active={selectedVehicleId === vehicle.id}
              onPress={() => setSelectedVehicleId(vehicle.id)}
            />
          ))}
        </View>

        <Text style={styles.label}>Type de panne</Text>
        <View style={styles.chipRow}>
          {TYPES_PANNE.map((type) => (
            <Chip key={type} label={type} active={typePanne === type} onPress={() => setTypePanne(type)} />
          ))}
        </View>

        <FormInput
          label="Description (optionnel)"
          value={description}
          onChangeText={setDescription}
          placeholder="Decrivez le probleme..."
          multiline
          numberOfLines={4}
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <PrimaryButton title="Confirmer la demande de RDV" onPress={handleSubmit} loading={submitting} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function Chip({ label, active, onPress }) {
  return (
    <Pressable style={[styles.chip, active && styles.chipActive]} onPress={onPress}>
      <Text style={[styles.chipText, active && styles.chipTextActive]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  centeredContent: { alignItems: 'center', justifyContent: 'center', padding: 24, gap: 16 },
  title: { fontSize: 20, fontWeight: '800', color: colors.text, marginBottom: 20 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8, marginTop: 4 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 18 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.text, fontWeight: '600' },
  chipTextActive: { color: '#fff' },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
  successTitle: { fontSize: 22, fontWeight: '800', color: colors.success },
  successText: { color: colors.textMuted, textAlign: 'center' },
});
