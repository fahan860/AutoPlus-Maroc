import { createNativeStackNavigator } from '@react-navigation/native-stack';
import GaragesScreen from '../screens/garages/GaragesScreen';
import GarageDetailScreen from '../screens/garages/GarageDetailScreen';
import BookInterventionScreen from '../screens/interventions/BookInterventionScreen';
import DescribeProblemScreen from '../screens/garages/DescribeProblemScreen';
import RecommendedGaragesScreen from '../screens/garages/RecommendedGaragesScreen';
import { colors } from '../theme/colors';

const Stack = createNativeStackNavigator();

export default function GaragesStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: colors.primary }}>
      <Stack.Screen name="GaragesList" component={GaragesScreen} options={{ title: 'Garages' }} />
      <Stack.Screen name="GarageDetail" component={GarageDetailScreen} options={{ title: 'Garage' }} />
      <Stack.Screen name="DescribeProblem" component={DescribeProblemScreen} options={{ title: 'Ma panne' }} />
      <Stack.Screen name="RecommendedGarages" component={RecommendedGaragesScreen} options={{ title: 'Garages conseillés' }} />
      <Stack.Screen
        name="BookIntervention"
        component={BookInterventionScreen}
        options={{ title: 'Prendre RDV' }}
      />
    </Stack.Navigator>
  );
}
