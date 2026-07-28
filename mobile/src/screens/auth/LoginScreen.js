import { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function LoginScreen({ navigation }) {
  const { login } = useAuth();
  const [identifiant, setIdentifiant] = useState('');
  const [motDePasse, setMotDePasse] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError('');
    if (!identifiant || !motDePasse) {
      setError('Telephone ou email, et mot de passe requis');
      return;
    }
    setLoading(true);
    try {
      await login(identifiant.trim(), motDePasse);
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
        <Text style={styles.title}>AUTO+</Text>
        <Text style={styles.subtitle}>Connectez-vous pour trouver un garage pres de chez vous</Text>

        <FormInput
          label="Telephone ou email"
          value={identifiant}
          onChangeText={setIdentifiant}
          placeholder="06 12 34 56 78 ou vous@exemple.com"
          autoCapitalize="none"
        />
        <FormInput
          label="Mot de passe"
          value={motDePasse}
          onChangeText={setMotDePasse}
          secureTextEntry
          placeholder="********"
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <PrimaryButton title="Se connecter" onPress={handleSubmit} loading={loading} />

        <PrimaryButton
          title="Creer un compte"
          variant="outline"
          onPress={() => navigation.navigate('Register')}
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 34, fontWeight: '800', color: colors.primary, textAlign: 'center' },
  subtitle: { fontSize: 15, color: colors.textMuted, textAlign: 'center', marginTop: 8, marginBottom: 32 },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
});
