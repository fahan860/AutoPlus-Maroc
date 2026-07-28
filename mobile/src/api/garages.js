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
