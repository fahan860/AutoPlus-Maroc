import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../context/AuthContext';
import AuthStack from './AuthStack';
import AppTabs from './AppTabs';
import GarageTabs from './GarageTabs';
import AdminTabs from './AdminTabs';
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

  // Routage par role : chaque type de compte a sa propre navigation
  // (voir docs/wireframes : ecran 1-4 = automobiliste, ecran 5 = mecanicien).
  if (user.role === 'mecanicien') return <GarageTabs />;
  if (user.role === 'admin') return <AdminTabs />;
  return <AppTabs />;
}
