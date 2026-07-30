import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../context/AuthContext';
import AuthStack from './AuthStack';
import AppTabs from './AppTabs';
import GarageTabs from './GarageTabs';
import VerifyEmailScreen from '../screens/auth/VerifyEmailScreen';
import CreateGarageScreen from '../screens/garage/CreateGarageScreen';
import { colors } from '../theme/colors';

export default function RootNavigator() {
  const { user, isBootstrapping } = useAuth();

  if (isBootstrapping) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.background }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!user) return <AuthStack />;

  // Compte non verifie : bloque l'acces au reste de l'app tant que le code
  // recu par email n'a pas ete valide.
  if (!user.email_verifie) return <VerifyEmailScreen />;

  // Routage par role : chaque type de compte a sa propre navigation
  // (voir docs/wireframes : ecran 1-4 = automobiliste, ecran 5 = mecanicien).
  if (user.role === 'mecanicien') {
    // Ni revendication choisie a l'inscription, ni garage cree depuis
    // CreateGarageScreen : on force la saisie des details du garage avant
    // d'acceder au tableau de bord.
    if (!user.garage_id) return <CreateGarageScreen />;
    return <GarageTabs />;
  }
  return <AppTabs />;
}
