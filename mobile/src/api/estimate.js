import { apiClient } from './client';

// Les listes (marques, modeles, villes) ne changent qu'avec une nouvelle version du
// modele : on les garde en memoire pour la duree de la session.
let optionsCache = null;

export async function getEstimateOptions() {
  if (!optionsCache) {
    const { data } = await apiClient.get('/vehicles/estimate/options');
    optionsCache = data;
  }
  return optionsCache;
}

// Estimation du prix d'un vehicule d'occasion (Modele A, service ML).
// Voir ml/service/schemas.py pour le detail des champs acceptes.
export function estimateVehicle(payload) {
  return apiClient.post('/vehicles/estimate', payload).then((res) => res.data);
}
