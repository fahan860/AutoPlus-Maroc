import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { setAuthToken, extractErrorMessage } from '../api/client';
import { login as loginRequest, register as registerRequest } from '../api/auth';

const TOKEN_KEY = 'autoplus_token';
const USER_KEY = 'autoplus_user';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [token, storedUser] = await Promise.all([
          SecureStore.getItemAsync(TOKEN_KEY),
          SecureStore.getItemAsync(USER_KEY),
        ]);
        if (token && storedUser) {
          setAuthToken(token);
          setUser(JSON.parse(storedUser));
        }
      } finally {
        setIsBootstrapping(false);
      }
    })();
  }, []);

  async function persistSession({ user: sessionUser, token }) {
    await Promise.all([
      SecureStore.setItemAsync(TOKEN_KEY, token),
      SecureStore.setItemAsync(USER_KEY, JSON.stringify(sessionUser)),
    ]);
    setAuthToken(token);
    setUser(sessionUser);
  }

  async function login(telephone, motDePasse) {
    const data = await loginRequest({ telephone, motDePasse });
    await persistSession(data);
  }

  async function register(nom, telephone, motDePasse, email, role, garageId, adminCode) {
    const data = await registerRequest({ nom, telephone, motDePasse, email, role, garageId, adminCode });
    await persistSession(data);
  }

  async function logout() {
    await Promise.all([SecureStore.deleteItemAsync(TOKEN_KEY), SecureStore.deleteItemAsync(USER_KEY)]);
    setAuthToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, isBootstrapping, login, register, logout }),
    [user, isBootstrapping]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth doit etre utilise a l\'interieur de AuthProvider');
  return ctx;
}

export { extractErrorMessage };
