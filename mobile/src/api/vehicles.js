import { apiClient } from './client';

export function listVehicles() {
  return apiClient.get('/vehicles').then((res) => res.data.vehicles);
}

export function addVehicle({ plaque, marque, modele, annee }) {
  return apiClient
    .post('/vehicles', { plaque, marque: marque || undefined, modele: modele || undefined, annee: annee || undefined })
    .then((res) => res.data);
}
