import { apiClient } from './client';

export function listGarages({ lat, lng, radiusKm, ville } = {}) {
  return apiClient
    .get('/garages', { params: { lat, lng, radius_km: radiusKm, ville } })
    .then((res) => res.data.garages);
}

export function getGarage(id) {
  return apiClient.get(`/garages/${id}`).then((res) => res.data);
}
