import { create } from 'zustand';

interface Marketplace {
  id: string;
  name: string;
  description: string;
  color: string;
  logoUrl?: string;
  type: string;
  priority: string;
  tags: string[];
  responsible: string;
  active: boolean;
  favorite: boolean;
  urls: {
    admin?: string;
    reports?: string;
    other?: string;
  };
  schedule: {
    start?: string;
    end?: string;
  };
  timezone: string;
  customFields: any[];
  createdAt?: string;
  updatedAt?: string;
  weeklyTasks: {
    total: number;
    completed: number;
    pending: number;
  };
}

interface MarketplaceFilters {
  type: string;
  priority: string;
  status: string;
  tags: string[];
  showFavorites: boolean;
}

interface MarketplaceState {
  marketplaces: Marketplace[];
  isLoading: boolean;
  error: string | null;
  filters: MarketplaceFilters;
  searchTerm: string;
  
  // Actions
  fetchMarketplaces: () => Promise<void>;
  createMarketplace: (marketplace: Partial<Marketplace>) => Promise<void>;
  updateMarketplace: (id: string, marketplace: Partial<Marketplace>) => Promise<void>;
  deleteMarketplace: (id: string) => Promise<void>;
  toggleFavorite: (id: string) => Promise<void>;
  toggleActive: (id: string) => Promise<void>;
  setFilters: (filters: Partial<MarketplaceFilters>) => void;
  setSearchTerm: (term: string) => void;
  clearError: () => void;
}

export const useMarketplaceStore = create<MarketplaceState>((set, get) => ({
  marketplaces: [],
  isLoading: false,
  error: null,
  filters: {
    type: 'all',
    priority: 'all',
    status: 'all',
    tags: [],
    showFavorites: false,
  },
  searchTerm: '',

  fetchMarketplaces: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const { filters, searchTerm } = get();
      const params: Record<string, string> = {};
      
      if (searchTerm) params.search = searchTerm;
      if (filters.type !== 'all') params.type = filters.type;
      if (filters.priority !== 'all') params.priority = filters.priority;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.showFavorites) params.favorites = 'true';

      const data = await marketplaceAPI.getAll(params);

      if (data.success) {
        set({ marketplaces: data.data, isLoading: false });
      } else {
        throw new Error(data.error || 'Erro ao buscar marketplaces');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        isLoading: false,
      });
    }
  },

  createMarketplace: async (marketplaceData) => {
    set({ isLoading: true, error: null });
    
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const data = await marketplaceAPI.create(marketplaceData);

      if (data.success) {
        const { marketplaces } = get();
        set({
          marketplaces: [...marketplaces, data.data],
          isLoading: false,
        });
      } else {
        throw new Error(data.error || 'Erro ao criar marketplace');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        isLoading: false,
      });
      throw error;
    }
  },

  updateMarketplace: async (id, marketplaceData) => {
    set({ isLoading: true, error: null });
    
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const data = await marketplaceAPI.update(id, marketplaceData);

      if (data.success) {
        const { marketplaces } = get();
        set({
          marketplaces: marketplaces.map(m => m.id === id ? data.data : m),
          isLoading: false,
        });
      } else {
        throw new Error(data.error || 'Erro ao atualizar marketplace');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteMarketplace: async (id) => {
    set({ isLoading: true, error: null });
    
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const data = await marketplaceAPI.delete(id);

      if (data.success) {
        const { marketplaces } = get();
        set({
          marketplaces: marketplaces.filter(m => m.id !== id),
          isLoading: false,
        });
      } else {
        throw new Error(data.error || 'Erro ao excluir marketplace');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        isLoading: false,
      });
      throw error;
    }
  },

  toggleFavorite: async (id) => {
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const data = await marketplaceAPI.toggleFavorite(id);

      if (data.success) {
        const { marketplaces } = get();
        set({
          marketplaces: marketplaces.map(m => m.id === id ? data.data : m),
        });
      } else {
        throw new Error(data.error || 'Erro ao alterar favorito');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      });
      throw error;
    }
  },

  toggleActive: async (id) => {
    try {
      const { marketplaceAPI } = await import('@/lib/api');
      const data = await marketplaceAPI.toggleActive(id);

      if (data.success) {
        const { marketplaces } = get();
        set({
          marketplaces: marketplaces.map(m => m.id === id ? data.data : m),
        });
      } else {
        throw new Error(data.error || 'Erro ao alterar status');
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      });
      throw error;
    }
  },

  setFilters: (newFilters) => {
    const { filters } = get();
    set({ filters: { ...filters, ...newFilters } });
  },

  setSearchTerm: (term) => {
    set({ searchTerm: term });
  },

  clearError: () => {
    set({ error: null });
  },
}));

