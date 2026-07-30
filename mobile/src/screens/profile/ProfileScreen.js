import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import { updateMe } from '../../api/auth';
import { getMonGarage, updateMonGarage } from '../../api/garages';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

const ROLE_LABELS = {
  automobiliste: 'Automobiliste',
  mecanicien: 'Mecanicien',
  admin: 'Administrateur',
};

export default function ProfileScreen() {
  const { user, updateUser, logout } = useAuth();

  const [adresse, setAdresse] = useState(user?.adresse || '');
  const [ville, setVille] = useState(user?.ville || '');
  const [savingProfil, setSavingProfil] = useState(false);
  const [profilMsg, setProfilMsg] = useState('');
  const [profilErr, setProfilErr] = useState('');

  const isMecanicien = user?.role === 'mecanicien';
  const [garage, setGarage] = useState(null);
  const [garageStatutMsg, setGarageStatutMsg] = useState('');
  const [garageForm, setGarageForm] = useState(null);
  const [savingGarage, setSavingGarage] = useState(false);
  const [garageErr, setGarageErr] = useState('');

  useEffect(() => {
    if (!isMecanicien) return;
    getMonGarage()
      .then((data) => {
        setGarage(data.garage);
        setGarageForm({
          nom: data.garage?.nom || '',
          categorie: data.garage?.categorie || '',
          adresse: data.garage?.adresse || '',
          ville: data.garage?.ville || '',
          telephone: data.garage?.telephone || '',
          services: data.garage?.services || '',
          horaires: data.garage?.horaires || '',
        });
      })
      .catch((err) => setGarageStatutMsg(extractErrorMessage(err)));
  }, [isMecanicien]);

  async function handleSaveProfil() {
    setProfilErr('');
    setProfilMsg('');
    setSavingProfil(true);
    try {
      const { user: updated } = await updateMe({ adresse: adresse.trim(), ville: ville.trim() });
      await updateUser(updated);
      setProfilMsg('Profil mis a jour');
    } catch (err) {
      setProfilErr(extractErrorMessage(err));
    } finally {
      setSavingProfil(false);
    }
  }

  async function handleSaveGarage() {
    setGarageErr('');
    setSavingGarage(true);
    try {
      const { garage: updated } = await updateMonGarage(garageForm);
      setGarage(updated);
    } catch (err) {
      setGarageErr(extractErrorMessage(err));
    } finally {
      setSavingGarage(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{user?.nom?.[0]?.toUpperCase() || '?'}</Text>
      </View>
      <Text style={styles.name}>{user?.nom}</Text>
      <Text style={styles.roleTag}>{ROLE_LABELS[user?.role] || user?.role}</Text>
      <Text style={styles.meta}>{user?.telephone}</Text>
      {user?.email ? <Text style={styles.meta}>{user.email}</Text> : null}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Mes informations</Text>
        <FormInput label="Adresse" value={adresse} onChangeText={setAdresse} placeholder="Votre adresse" />
        <FormInput label="Ville" value={ville} onChangeText={setVille} placeholder="Votre ville" />
        {profilErr ? <Text style={styles.error}>{profilErr}</Text> : null}
        {profilMsg ? <Text style={styles.success}>{profilMsg}</Text> : null}
        <PrimaryButton title="Enregistrer" onPress={handleSaveProfil} loading={savingProfil} />
      </View>

      {isMecanicien ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Mon garage</Text>
          {garageStatutMsg ? <Text style={styles.hint}>{garageStatutMsg}</Text> : null}
          {garageForm ? (
            <>
              <FormInput label="Nom du garage" value={garageForm.nom} onChangeText={(v) => setGarageForm({ ...garageForm, nom: v })} />
              <FormInput label="Categorie" value={garageForm.categorie} onChangeText={(v) => setGarageForm({ ...garageForm, categorie: v })} />
              <FormInput label="Adresse" value={garageForm.adresse} onChangeText={(v) => setGarageForm({ ...garageForm, adresse: v })} />
              <FormInput label="Ville" value={garageForm.ville} onChangeText={(v) => setGarageForm({ ...garageForm, ville: v })} />
              <FormInput label="Telephone" value={garageForm.telephone} onChangeText={(v) => setGarageForm({ ...garageForm, telephone: v })} keyboardType="phone-pad" />
              <FormInput label="Services proposes" value={garageForm.services} onChangeText={(v) => setGarageForm({ ...garageForm, services: v })} />
              <FormInput label="Horaires" value={garageForm.horaires} onChangeText={(v) => setGarageForm({ ...garageForm, horaires: v })} />
              {garageErr ? <Text style={styles.error}>{garageErr}</Text> : null}
              <PrimaryButton title="Enregistrer le garage" onPress={handleSaveGarage} loading={savingGarage} />
            </>
          ) : null}
        </View>
      ) : null}

      <View style={styles.spacer} />

      <PrimaryButton title="Se deconnecter" variant="outline" onPress={logout} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: colors.background, alignItems: 'center', padding: 24, paddingTop: 48 },
  avatar: {
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  avatarText: { color: '#fff', fontSize: 32, fontWeight: '800' },
  name: { fontSize: 20, fontWeight: '700', color: colors.text },
  roleTag: { fontSize: 12, fontWeight: '700', color: colors.primary, marginTop: 4, textTransform: 'uppercase' },
  meta: { color: colors.textMuted, marginTop: 4 },
  section: { width: '100%', marginTop: 28 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: colors.text, marginBottom: 12 },
  hint: { fontSize: 12, color: colors.textMuted, marginBottom: 10 },
  error: { color: colors.danger, marginBottom: 10, textAlign: 'center' },
  success: { color: colors.primary, marginBottom: 10, textAlign: 'center' },
  spacer: { height: 24 },
});
