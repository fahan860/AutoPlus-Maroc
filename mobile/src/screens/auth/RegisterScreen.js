import { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [email, setEmail] = useState('');
  const [motDePasse, setMotDePasse] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError('');
    if (!nom || !telephone || !motDePasse) {
      setError('Nom, telephone et mot de passe sont requis');
      return;
    }
    if (motDePasse.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caracteres');
      return;
    }
    setLoading(true);
    try {
      await register(nom.trim(), telephone.trim(), motDePasse, email.trim() || undefined);
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
        <Text style={styles.subtitle}>Rejoignez AUTO+ en tant qu'automobiliste</Text>

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
          label="Email (optionnel)"
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
          placeholder="6 caracteres minimum"
        />

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
  subtitle: { fontSize: 15, color: colors.textMuted, textAlign: 'center', marginTop: 8, marginBottom: 28 },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
});
