import { View, Text, StyleSheet } from 'react-native';
import { useAuth } from '../../context/AuthContext';
import PrimaryButton from '../../components/PrimaryButton';
import { colors } from '../../theme/colors';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  return (
    <View style={styles.container}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{user?.nom?.[0]?.toUpperCase() || '?'}</Text>
      </View>
      <Text style={styles.name}>{user?.nom}</Text>
      <Text style={styles.meta}>{user?.telephone}</Text>
      {user?.email ? <Text style={styles.meta}>{user.email}</Text> : null}

      <View style={styles.spacer} />

      <PrimaryButton title="Se deconnecter" variant="outline" onPress={logout} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, alignItems: 'center', padding: 24, paddingTop: 48 },
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
  meta: { color: colors.textMuted, marginTop: 4 },
  spacer: { height: 32 },
});
