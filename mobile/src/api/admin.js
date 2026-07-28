import { apiClient } from './client';

export function listMecaniciensEnAttente() {
  return apiClient.get('/admin/mecaniciens/pending').then((res) => res.data.mecaniciens);
}

export function validerMecanicien(userId, statut) {
  return apiClient.patch(`/admin/mecaniciens/${userId}/statut`, { statut }).then((res) => res.data);
}

export function listUsers(role) {
  return apiClient.get('/admin/users', { params: { role } }).then((res) => res.data.users);
}

export function setUserActif(userId, actif) {
  return apiClient.patch(`/admin/users/${userId}/actif`, { actif }).then((res) => res.data);
}
