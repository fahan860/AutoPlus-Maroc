import { apiClient } from './client';

export function register({ nom, telephone, email, motDePasse, role, garageId }) {
  return apiClient
    .post('/users/register', {
      nom,
      telephone,
      email,
      mot_de_passe: motDePasse,
      role: role || undefined,
      garage_id: garageId || undefined,
    })
    .then((res) => res.data);
}

export function login({ identifiant, motDePasse }) {
  return apiClient
    .post('/users/login', { identifiant, mot_de_passe: motDePasse })
    .then((res) => res.data);
}

export function verifyEmail(code) {
  return apiClient.post('/users/verify-email', { code }).then((res) => res.data);
}

export function resendVerificationCode() {
  return apiClient.post('/users/resend-code').then((res) => res.data);
}

export function updateMe({ adresse, ville }) {
  return apiClient.patch('/users/me', { adresse, ville }).then((res) => res.data);
}
