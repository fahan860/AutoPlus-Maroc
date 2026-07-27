import { apiClient } from './client';

export function register({ nom, telephone, email, motDePasse }) {
  return apiClient
    .post('/users/register', { nom, telephone, email: email || undefined, mot_de_passe: motDePasse })
    .then((res) => res.data);
}

export function login({ telephone, motDePasse }) {
  return apiClient
    .post('/users/login', { telephone, mot_de_passe: motDePasse })
    .then((res) => res.data);
}
