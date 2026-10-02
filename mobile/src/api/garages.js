import { apiClient } from './client';

export function listGarages({ lat, lng, radiusKm, ville } = {}) {
  return apiClient
    .get('/garages', { params: { lat, lng, radius_km: radiusKm, ville } })
    .then((res) => res.data.garages);
}

export function getGarage(id) {
  return apiClient.get(`/garages/${id}`).then((res) => res.data);
}

// Cote garagiste : son propre garage + compteurs de RDV par statut
export function getMonGarage() {
  return apiClient.get('/garages/mine').then((res) => res.data);
}

export function getMesVehiculesGarage() {
  return apiClient.get('/garages/mine/vehicules').then((res) => res.data.vehicules);
}

// Creation du garage par le mecanicien lui-meme (alternative a la revendication
// d'une fiche existante lors de l'inscription).
export function createMonGarage(payload) {
  return apiClient.post('/garages/mine', payload).then((res) => res.data);
}

export function updateMonGarage(payload) {
  return apiClient.patch('/garages/mine', payload).then((res) => res.data);
}

// Recommandation de garages a partir d'une panne decrite en texte libre (Modele B).
// Voir ml/service/schemas.py pour le format de la reponse.
export function recommendGarages({ description, lat, lon, nbGarages = 5 }) {
  return apiClient
    .post('/garages/recommend', { description, lat, lon, nb_garages: nbGarages })
    .then((res) => res.data);
}
