import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AssistantScreen from '../screens/assistant/AssistantScreen';
import ConversationsScreen from '../screens/assistant/ConversationsScreen';
import { colors } from '../theme/colors';

const Stack = createNativeStackNavigator();

export default function AssistantStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: colors.primary }}>
      <Stack.Screen name="AssistantChat" component={AssistantScreen} options={{ title: 'Assistant AUTO+' }} />
      <Stack.Screen name="Conversations" component={ConversationsScreen} options={{ title: 'Historique' }} />
    </Stack.Navigator>
  );
}
