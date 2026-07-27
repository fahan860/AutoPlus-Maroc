import { apiClient } from './client';

export function listInterventions() {
  return apiClient.get('/interventions').then((res) => res.data.interventions);
}

export function createIntervention({ vehicleId, garageId, typePanne, description, dateRdv }) {
  return apiClient
    .post('/interventions', {
      vehicle_id: vehicleId,
      garage_id: garageId,
      type_panne: typePanne || undefined,
      description: description || undefined,
      date_rdv: dateRdv || undefined,
    })
    .then((res) => res.data);
}
