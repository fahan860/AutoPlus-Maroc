import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Pressable,
} from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import { listGarages } from '../../api/garages';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import PasswordRequirements, { isPasswordValid } from '../../components/PasswordRequirements';
import { colors } from '../../theme/colors';

const ROLES = [
  { value: 'automobiliste', label: 'Automobiliste' },
  { value: 'mecanicien', label: 'Mécanicien' },
];

export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [email, setEmail] = useState('');
  const [motDePasse, setMotDePasse] = useState('');
  const [role, setRole] = useState('automobiliste');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Selection d'un garage existant a revendiquer (role mecanicien uniquement)
  const [garages, setGarages] = useState([]);
  const [garagesLoading, setGaragesLoading] = useState(false);
  const [garageSearch, setGarageSearch] = useState('');
  const [selectedGarage, setSelectedGarage] = useState(null);

  useEffect(() => {
    if (role !== 'mecanicien' || garages.length) return;
    setGaragesLoading(true);
    listGarages()
      .then(setGarages)
      .catch(() => {})
      .finally(() => setGaragesLoading(false));
  }, [role]);

  const filteredGarages = garages.filter((g) =>
    g.nom.toLowerCase().includes(garageSearch.trim().toLowerCase())
  );

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  async function handleSubmit() {
    setError('');
    if (!nom || !telephone || !email || !motDePasse) {
      setError('Nom, telephone, email et mot de passe sont requis');
      return;
    }
    if (!isValidEmail(email.trim())) {
      setError('Adresse email invalide');
      return;
    }
    if (!isPasswordValid(motDePasse)) {
      setError('Le mot de passe ne respecte pas les critères de sécurité ci-dessous');
      return;
    }
    if (role === 'mecanicien' && !selectedGarage) {
      setError('Choisissez le garage que vous representez');
      return;
    }

    setLoading(true);
    try {
      await register(
        nom.trim(),
        telephone.trim(),
        motDePasse,
        email.trim(),
        role,
        selectedGarage?.id
      );
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
        <Text style={styles.title}>Creer un compte</Text>
        <Text style={styles.subtitle}>Rejoignez AUTO+</Text>

        <Text style={styles.label}>Je suis</Text>
        <View style={styles.roleRow}>
          {ROLES.map((r) => (
            <Pressable
              key={r.value}
              onPress={() => {
                setRole(r.value);
                setSelectedGarage(null);
              }}
              style={[styles.roleChip, role === r.value && styles.roleChipActive]}
            >
              <Text style={[styles.roleChipText, role === r.value && styles.roleChipTextActive]}>
                {r.label}
              </Text>
            </Pressable>
          ))}
        </View>

        <FormInput label="Nom complet" value={nom} onChangeText={setNom} placeholder="Votre nom" />
        <FormInput
          label="Telephone"
          value={telephone}
          onChangeText={setTelephone}
          keyboardType="phone-pad"
          placeholder="06 12 34 56 78"
          autoCapitalize="none"
        />
        <FormInput
          label="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          placeholder="vous@exemple.com"
        />
        <FormInput
          label="Mot de passe"
          value={motDePasse}
          onChangeText={setMotDePasse}
          secureTextEntry
          placeholder="Votre mot de passe"
        />
        <PasswordRequirements password={motDePasse} />

        {role === 'mecanicien' ? (
          <View style={styles.garagePicker}>
            <Text style={styles.label}>Votre garage (base existante)</Text>
            <Text style={styles.hint}>
              Choisissez le garage que vous representez. Un admin doit valider la demande avant
              l'acces au tableau de bord.
            </Text>
            {selectedGarage ? (
              <Pressable style={styles.selectedGarage} onPress={() => setSelectedGarage(null)}>
                <Text style={styles.selectedGarageText}>{selectedGarage.nom}</Text>
                <Text style={styles.selectedGarageChange}>Changer</Text>
              </Pressable>
            ) : (
              <>
                <FormInput
                  placeholder="Rechercher un garage par nom..."
                  value={garageSearch}
                  onChangeText={setGarageSearch}
                />
                {garagesLoading ? (
                  <Text style={styles.hint}>Chargement des garages...</Text>
                ) : (
                  <View style={styles.garageList}>
                    {filteredGarages.slice(0, 8).length === 0 ? (
                      <Text style={styles.hint}>Aucun garage trouve</Text>
                    ) : (
                      filteredGarages.slice(0, 8).map((item) => (
                        <Pressable
                          key={item.id}
                          style={styles.garageRow}
                          onPress={() => setSelectedGarage(item)}
                        >
                          <Text style={styles.garageRowText}>{item.nom}</Text>
                          <Text style={styles.garageRowSub}>{item.ville}</Text>
                        </Pressable>
                      ))
                    )}
                  </View>
                )}
              </>
            )}
          </View>
        ) : null}

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <PrimaryButton title="Creer mon compte" onPress={handleSubmit} loading={loading} />

        <PrimaryButton title="J'ai deja un compte" variant="outline" onPress={() => navigation.goBack()} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 28, fontWeight: '800', color: colors.primary, textAlign: 'center' },
  subtitle: { fontSize: 15, color: colors.textMuted, textAlign: 'center', marginTop: 8, marginBottom: 20 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8 },
  hint: { fontSize: 12, color: colors.textMuted, marginBottom: 10 },
  roleRow: { flexDirection: 'row', gap: 8, marginBottom: 18 },
  roleChip: {
    flex: 1,
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  roleChipActive: { borderColor: colors.primary, backgroundColor: colors.primary },
  roleChipText: { fontSize: 13, fontWeight: '600', color: colors.text },
  roleChipTextActive: { color: '#fff' },
  garagePicker: { marginBottom: 14 },
  garageList: { borderWidth: 1, borderColor: colors.border, borderRadius: 10, overflow: 'hidden' },
  garageRow: {
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  garageRowText: { fontSize: 15, color: colors.text, fontWeight: '600' },
  garageRowSub: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  selectedGarage: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: colors.primary,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  selectedGarageText: { fontSize: 15, fontWeight: '700', color: colors.text },
  selectedGarageChange: { fontSize: 13, color: colors.primary, fontWeight: '600' },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
});
