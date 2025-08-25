import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  username: string;
  email: string;
  name?: string;
  avatarUrl?: string;
  role: string;
  active: boolean;
  timezone: string;
  notificationsEnabled: boolean;
  initials: string;
  createdAt?: string;
  updatedAt?: string;
  lastLogin?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: { username?: string; email?: string; password: string }) => Promise<void>;
  register: (userData: { username: string; email: string; password: string; name?: string }) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const { authAPI } = await import('@/lib/api');
          const data = await authAPI.login(credentials);

          if (data.success) {
            set({
              user: data.data.user,
              token: data.data.token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            throw new Error(data.error || 'Erro ao fazer login');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Erro desconhecido',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        
        try {
          const { authAPI } = await import('@/lib/api');
          const data = await authAPI.register(userData);

          if (data.success) {
            set({
              user: data.data.user,
              token: data.data.token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            throw new Error(data.error || 'Erro ao criar conta');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Erro desconhecido',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      setUser: (user) => {
        set({ user, isAuthenticated: true });
      },

      setToken: (token) => {
        set({ token });
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

