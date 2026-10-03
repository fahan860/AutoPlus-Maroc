import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import GaragesStack from './GaragesStack';
import VehiclesStack from './VehiclesStack';
import MyInterventionsScreen from '../screens/interventions/MyInterventionsScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import AssistantStack from './AssistantStack';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();

const ICONS = {
  Garages: '🔧',
  Assistant: '🤖',
  Vehicules: '🚗',
  'Mes RDV': '📅',
  Profil: '👤',
};

function TabIcon({ route, focused }) {
  return <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.5 }}>{ICONS[route.name]}</Text>;
}

export default function AppTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarIcon: ({ focused }) => <TabIcon route={route} focused={focused} />,
      })}
    >
      <Tab.Screen name="Garages" component={GaragesStack} />
      <Tab.Screen
        name="Assistant"
        component={AssistantStack}
      />
      <Tab.Screen name="Vehicules" component={VehiclesStack} options={{ title: 'Véhicules' }} />
      <Tab.Screen
        name="Mes RDV"
        component={MyInterventionsScreen}
        options={{ headerShown: true, headerTintColor: colors.primary }}
      />
      <Tab.Screen
        name="Profil"
        component={ProfileScreen}
        options={{ headerShown: true, headerTintColor: colors.primary }}
      />
    </Tab.Navigator>
  );
}
