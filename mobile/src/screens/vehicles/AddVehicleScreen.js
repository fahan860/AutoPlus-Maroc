import { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { addVehicle } from '../../api/vehicles';
import { extractErrorMessage } from '../../api/client';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function AddVehicleScreen({ navigation }) {
  const [plaque, setPlaque] = useState('');
  const [marque, setMarque] = useState('');
  const [modele, setModele] = useState('');
  const [annee, setAnnee] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError('');
    if (!plaque.trim()) {
      setError('La plaque d\'immatriculation est requise');
      return;
    }
    setLoading(true);
    try {
      await addVehicle({
        plaque: plaque.trim(),
        marque: marque.trim(),
        modele: modele.trim(),
        annee: annee ? Number(annee) : undefined,
      });
      navigation.goBack();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <FormInput
          label="Plaque d'immatriculation"
          value={plaque}
          onChangeText={setPlaque}
          placeholder="12345-A-6"
          autoCapitalize="characters"
        />
        <FormInput label="Marque" value={marque} onChangeText={setMarque} placeholder="Ex : Dacia" />
        <FormInput label="Modele" value={modele} onChangeText={setModele} placeholder="Ex : Logan" />
        <FormInput
          label="Annee"
          value={annee}
          onChangeText={setAnnee}
          placeholder="Ex : 2019"
          keyboardType="number-pad"
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <PrimaryButton title="Enregistrer le vehicule" onPress={handleSubmit} loading={loading} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
});
