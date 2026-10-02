import { apiClient } from './client';

// Un tour de conversation avec l'assistant IA (ml/src/agent/agent.py). L'historique complet est
// renvoye a chaque message : le service est sans etat. Pour les messages de l'assistant, `action`
// permet au service de compter les questions deja posees.
export function sendAgentMessage({ messages, vehicule, lat, lon }) {
  return apiClient
    .post('/agent/chat', {
      messages: messages.map(({ role, content, action }) => (action ? { role, content, action } : { role, content })),
      vehicule: vehicule || undefined,
      lat,
      lon,
    })
    .then((res) => res.data);
}
