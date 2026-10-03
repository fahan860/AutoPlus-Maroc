import Constants from 'expo-constants';

// En dev (Expo Go), on derive l'IP LAN de la machine depuis l'URL du bundler
// (hostUri, ex: "192.168.1.23:8081") pour que ca marche sur un telephone
// physique sans configuration manuelle. Override possible via app.json > extra.apiUrl.
function resolveApiBaseUrl() {
  const configured = Constants.expoConfig?.extra?.apiUrl;
  if (configured) return configured;

  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) {
    const host = hostUri.split(':')[0];
    return `http://${host}:3000`;
  }

  return 'http://localhost:3000';
}

export const API_BASE_URL = resolveApiBaseUrl();

let authToken = null;

export function setAuthToken(token) {
  authToken = token || null;
}

function buildUrl(path, params) {
  const url = new URL(path, API_BASE_URL);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) url.searchParams.set(key, value);
    });
  }
  return url.toString();
}

async function request(method, path, { data, params } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  let response;
  try {
    response = await fetch(buildUrl(path, params), {
      method,
      headers,
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  } catch {
    throw new Error('Impossible de contacter le serveur. Verifiez votre connexion.');
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // reponse sans corps JSON (ex: 204) : on garde body a null
  }

  if (!response.ok) {
    const error = new Error(body?.message || `Erreur ${response.status}`);
    error.response = { status: response.status, data: body };
    throw error;
  }

  return { data: body };
}

// Client HTTP minimal base sur fetch (au lieu d'axios : Metro resout mal les
// methodes d'instance d'axios sur React Native, voir historique du commit).
export const apiClient = {
  get: (path, config) => request('GET', path, config),
  post: (path, data) => request('POST', path, { data }),
  patch: (path, data) => request('PATCH', path, { data }),
  delete: (path) => request('DELETE', path),
};

// Normalise les erreurs API en un message affichable directement dans l'UI
export function extractErrorMessage(err) {
  return err?.response?.data?.message || err?.message || 'Erreur inconnue';
}
