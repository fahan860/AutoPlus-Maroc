import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import GarageDashboardScreen from '../screens/garage/GarageDashboardScreen';
import GarageVehiclesScreen from '../screens/garage/GarageVehiclesScreen';
import GarageReviewsScreen from '../screens/garage/GarageReviewsScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();

const ICONS = {
  'Tableau de bord': '📋',
  Vehicules: '🚗',
  Avis: '⭐',
  Profil: '⚙️',
};

function TabIcon({ route, focused }) {
  return <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.5 }}>{ICONS[route.name]}</Text>;
}

// Navigation du compte "mecanicien" : cf. wireframe "5. Dashboard Garagiste"
// (Tableau de bord, Demandes de RDV, Vehicules, Avis clients, Parametres).
export default function GarageTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarIcon: ({ focused }) => <TabIcon route={route} focused={focused} />,
        headerShown: true,
        headerTintColor: colors.primary,
      })}
    >
      <Tab.Screen name="Tableau de bord" component={GarageDashboardScreen} />
      <Tab.Screen name="Vehicules" component={GarageVehiclesScreen} options={{ title: 'Véhicules' }} />
      <Tab.Screen name="Avis" component={GarageReviewsScreen} options={{ title: 'Avis clients' }} />
      <Tab.Screen name="Profil" component={ProfileScreen} options={{ title: 'Paramètres' }} />
    </Tab.Navigator>
  );
}
