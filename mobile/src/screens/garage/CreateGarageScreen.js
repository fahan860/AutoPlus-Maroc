import { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import { createMonGarage } from '../../api/garages';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

// Affiche quand role === 'mecanicien' et que le compte n'a pas encore de
// garage rattache (ni revendication a l'inscription, ni creation depuis
// cet ecran). Voir RootNavigator.
export default function CreateGarageScreen() {
  const { user, updateUser, logout } = useAuth();
  const [nom, setNom] = useState('');
  const [categorie, setCategorie] = useState('');
  const [adresse, setAdresse] = useState('');
  const [ville, setVille] = useState('');
  const [telephone, setTelephone] = useState('');
  const [services, setServices] = useState('');
  const [horaires, setHoraires] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError('');
    if (!nom.trim()) {
      setError('Le nom du garage est requis');
      return;
    }
    setLoading(true);
    try {
      await createMonGarage({
        nom: nom.trim(),
        categorie: categorie.trim() || undefined,
        adresse: adresse.trim() || undefined,
        ville: ville.trim() || undefined,
        telephone: telephone.trim() || undefined,
        services: services.trim() || undefined,
        horaires: horaires.trim() || undefined,
      });
      // On ne connait pas encore l'id garantie retourne par le serveur cote
      // client sans un aller-retour supplementaire : on marque simplement le
      // compte comme "garage en attente" pour debloquer le dashboard, qui
      // affichera lui-meme l'etat "en attente de validation".
      await updateUser({ ...user, garage_id: -1, garage_statut: 'en_attente' });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Votre garage</Text>
        <Text style={styles.subtitle}>
          Ce garage n'existe pas encore dans notre annuaire : renseignez ses infos. Un admin
          valide votre demande avant l'acces au tableau de bord.
        </Text>

        <FormInput label="Nom du garage" value={nom} onChangeText={setNom} placeholder="Ex: Garage Al Amal" />
        <FormInput
          label="Categorie"
          value={categorie}
          onChangeText={setCategorie}
          placeholder="Ex: Mecanique generale, carrosserie..."
        />
        <FormInput label="Adresse" value={adresse} onChangeText={setAdresse} placeholder="Rue, quartier..." />
        <FormInput label="Ville" value={ville} onChangeText={setVille} placeholder="Casablanca" />
        <FormInput
          label="Telephone du garage"
          value={telephone}
          onChangeText={setTelephone}
          keyboardType="phone-pad"
          placeholder="05 22 00 00 00"
        />
        <FormInput
          label="Services proposes"
          value={services}
          onChangeText={setServices}
          placeholder="Vidange, freins, climatisation..."
        />
        <FormInput
          label="Horaires"
          value={horaires}
          onChangeText={setHoraires}
          placeholder="Lun-Sam 8h-19h"
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <PrimaryButton title="Enregistrer mon garage" onPress={handleSubmit} loading={loading} />
        <PrimaryButton title="Se deconnecter" variant="outline" onPress={logout} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flexGrow: 1, padding: 24, paddingTop: 48 },
  title: { fontSize: 24, fontWeight: '800', color: colors.primary, textAlign: 'center' },
  subtitle: { fontSize: 13, color: colors.textMuted, textAlign: 'center', marginTop: 8, marginBottom: 20 },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
});
