import { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { useAuth, extractErrorMessage } from '../../context/AuthContext';
import { verifyEmail, resendVerificationCode } from '../../api/auth';
import FormInput from '../../components/FormInput';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

// Affiche tant que user.email_verifie === false (voir RootNavigator). Bloque
// l'acces au reste de l'app jusqu'a saisie du code recu par email.
export default function VerifyEmailScreen() {
  const { user, updateUser, logout } = useAuth();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  async function handleVerify() {
    setError('');
    setInfo('');
    if (code.trim().length !== 6) {
      setError('Le code contient 6 chiffres');
      return;
    }
    setLoading(true);
    try {
      const { user: updated } = await verifyEmail(code.trim());
      await updateUser(updated);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setError('');
    setInfo('');
    setResending(true);
    try {
      await resendVerificationCode();
      setInfo('Un nouveau code a ete envoye a ' + (user?.email || 'votre adresse email'));
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setResending(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.container}>
        <Text style={styles.title}>Verifiez votre email</Text>
        <Text style={styles.subtitle}>
          Un code a 6 chiffres a ete envoye a{'\n'}
          <Text style={styles.email}>{user?.email}</Text>
        </Text>

        <FormInput
          label="Code de verification"
          value={code}
          onChangeText={setCode}
          keyboardType="number-pad"
          maxLength={6}
          placeholder="000000"
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}
        {info ? <Text style={styles.info}>{info}</Text> : null}

        <PrimaryButton title="Valider" onPress={handleVerify} loading={loading} />
        <PrimaryButton
          title="Renvoyer le code"
          variant="outline"
          onPress={handleResend}
          loading={resending}
        />
        <PrimaryButton title="Se deconnecter" variant="outline" onPress={logout} />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flex: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: '800', color: colors.primary, textAlign: 'center' },
  subtitle: { fontSize: 14, color: colors.textMuted, textAlign: 'center', marginTop: 8, marginBottom: 24 },
  email: { fontWeight: '700', color: colors.text },
  error: { color: colors.danger, marginBottom: 14, textAlign: 'center' },
  info: { color: colors.primary, marginBottom: 14, textAlign: 'center' },
});
