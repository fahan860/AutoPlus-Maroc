import { apiClient } from './client';

// Un tour de conversation avec l'assistant IA (ml/src/agent/agent.py). L'historique complet est
// renvoye a chaque message : le service est sans etat. Pour les messages de l'assistant, `action`
// permet au service de compter les questions deja posees. La reponse contient `conversation_id` :
// le renvoyer au message suivant pour continuer la meme conversation dans l'historique.
export function sendAgentMessage({ conversationId, messages, vehicule, lat, lon }) {
  return apiClient
    .post('/agent/chat', {
      conversation_id: conversationId || undefined,
      messages: messages.map(({ role, content, action }) => (action ? { role, content, action } : { role, content })),
      vehicule: vehicule || undefined,
      lat,
      lon,
    })
    .then((res) => res.data);
}

// Historique des conversations de l'utilisateur connecte
export function listConversations() {
  return apiClient.get('/agent/conversations').then((res) => res.data.conversations);
}

export function getConversation(id) {
  return apiClient.get(`/agent/conversations/${id}`).then((res) => res.data);
}

export function deleteConversation(id) {
  return apiClient.delete(`/agent/conversations/${id}`);
}
