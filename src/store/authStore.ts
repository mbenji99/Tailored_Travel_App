import { create } from 'zustand';

interface AuthUser {
  id: string;
  email: string;
}

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  setUser: (user: AuthUser | null) => void;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,

  signIn: async (email, password) => {
    const res = await fetch(`${API_URL}/login`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Login failed');

    set({ user: data.user });
  },

  signUp: async (email, password) => {
    const res = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Registration failed');

    set({ user: data.user });
  },

  signOut: async () => {
    await fetch(`${API_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    set({ user: null });
  },

  setUser: (user) => set({ user, loading: false }),
}));
