import { createNativeStackNavigator } from '@react-navigation/native-stack';
import VehiclesScreen from '../screens/vehicles/VehiclesScreen';
import AddVehicleScreen from '../screens/vehicles/AddVehicleScreen';
import EstimateVehicleScreen from '../screens/vehicles/EstimateVehicleScreen';
import EstimateResultScreen from '../screens/vehicles/EstimateResultScreen';
import { colors } from '../theme/colors';

const Stack = createNativeStackNavigator();

export default function VehiclesStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: colors.primary }}>
      <Stack.Screen name="VehiclesList" component={VehiclesScreen} options={{ title: 'Mes vehicules' }} />
      <Stack.Screen name="AddVehicle" component={AddVehicleScreen} options={{ title: 'Ajouter un vehicule' }} />
      <Stack.Screen name="EstimateVehicle" component={EstimateVehicleScreen} options={{ title: 'Estimer mon véhicule' }} />
      <Stack.Screen name="EstimateResult" component={EstimateResultScreen} options={{ title: 'Estimation' }} />
    </Stack.Navigator>
  );
}
