import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AdminPendingScreen from '../screens/admin/AdminPendingScreen';
import AdminUsersScreen from '../screens/admin/AdminUsersScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();

const ICONS = {
  'Garages en attente': '🕓',
  Utilisateurs: '👥',
  Profil: '⚙️',
};

function TabIcon({ route, focused }) {
  return <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.5 }}>{ICONS[route.name]}</Text>;
}

export default function AdminTabs() {
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
      <Tab.Screen name="Garages en attente" component={AdminPendingScreen} options={{ title: 'Revendications' }} />
      <Tab.Screen name="Utilisateurs" component={AdminUsersScreen} />
      <Tab.Screen name="Profil" component={ProfileScreen} options={{ title: 'Paramètres' }} />
    </Tab.Navigator>
  );
}
