import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { MarketplaceForm } from "@/components/marketplaces/MarketplaceForm";
import { MarketplaceGrid } from "@/components/marketplaces/MarketplaceGrid";
import { MarketplaceFilters } from "@/components/marketplaces/MarketplaceFilters";
import { useToast } from "@/hooks/use-toast";
import { useMarketplaceStore } from "@/store/marketplaceStore";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";

const Marketplaces = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [editingMarketplace, setEditingMarketplace] = useState(null);
  const [viewMode, setViewMode] = useState<'cards' | 'list'>('cards');

  const {
    marketplaces,
    isLoading,
    error,
    filters,
    searchTerm,
    fetchMarketplaces,
    createMarketplace,
    updateMarketplace,
    deleteMarketplace,
    toggleFavorite,
    toggleActive,
    setFilters,
    setSearchTerm,
    clearError,
  } = useMarketplaceStore();

  const { toast } = useToast();

  // Get all unique tags from marketplaces
  const availableTags = Array.from(new Set(marketplaces.flatMap(m => m.tags)));

  // Filter marketplaces based on search and filters
  const filteredMarketplaces = marketplaces.filter(marketplace => {
    const matchesSearch = marketplace.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         marketplace.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         marketplace.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesType = filters.type === 'all' || marketplace.type === filters.type;
    const matchesPriority = filters.priority === 'all' || marketplace.priority === filters.priority;
    const matchesStatus = filters.status === 'all' || 
                         (filters.status === 'active' && marketplace.active) ||
                         (filters.status === 'inactive' && !marketplace.active);
    const matchesTags = filters.tags.length === 0 || 
                       filters.tags.some(tag => marketplace.tags.includes(tag));
    const matchesFavorites = !filters.showFavorites || marketplace.favorite;

    return matchesSearch && matchesType && matchesPriority && matchesStatus && matchesTags && matchesFavorites;
  });

  // Load marketplaces on component mount
  useEffect(() => {
    fetchMarketplaces();
  }, [fetchMarketplaces]);

  // Refetch when filters or search term change
  useEffect(() => {
    fetchMarketplaces();
  }, [filters, searchTerm, fetchMarketplaces]);

  // Clear error when component unmounts
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  const handleSave = async (marketplaceData) => {
    try {
      if (editingMarketplace) {
        await updateMarketplace(editingMarketplace.id, marketplaceData);
        toast({
          title: "Marketplace atualizado",
          description: `${marketplaceData.name} foi atualizado com sucesso.`,
        });
      } else {
        await createMarketplace(marketplaceData);
        toast({
          title: "Marketplace criado",
          description: `${marketplaceData.name} foi criado com sucesso.`,
        });
      }
      setFormOpen(false);
      setEditingMarketplace(null);
    } catch (error) {
      toast({
        title: "Erro",
        description: error.message || "Ocorreu um erro inesperado.",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (marketplace) => {
    setEditingMarketplace(marketplace);
    setFormOpen(true);
  };

  const handleDuplicate = async (marketplace) => {
    try {
      const duplicated = {
        ...marketplace,
        id: `${marketplace.id}-copy-${Date.now()}`,
        name: `${marketplace.name} (Cópia)`,
      };
      delete duplicated.createdAt;
      delete duplicated.updatedAt;
      delete duplicated.weeklyTasks;
      
      await createMarketplace(duplicated);
      toast({
        title: "Marketplace duplicado",
        description: `${duplicated.name} foi criado com sucesso.`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao duplicar marketplace.",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (marketplace) => {
    try {
      await deleteMarketplace(marketplace.id);
      toast({
        title: "Marketplace removido",
        description: `${marketplace.name} foi removido com sucesso.`,
        variant: "destructive",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao remover marketplace.",
        variant: "destructive",
      });
    }
  };

  const handleToggleFavorite = async (marketplace) => {
    try {
      await toggleFavorite(marketplace.id);
      toast({
        title: marketplace.favorite ? "Removido dos favoritos" : "Adicionado aos favoritos",
        description: `${marketplace.name} foi ${marketplace.favorite ? 'removido dos' : 'adicionado aos'} favoritos.`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao alterar favorito.",
        variant: "destructive",
      });
    }
  };

  const handleToggleActive = async (marketplace) => {
    try {
      await toggleActive(marketplace.id);
      toast({
        title: marketplace.active ? "Marketplace desativado" : "Marketplace ativado",
        description: `${marketplace.name} foi ${marketplace.active ? 'desativado' : 'ativado'}.`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao alterar status.",
        variant: "destructive",
      });
    }
  };

  const handleClearFilters = () => {
    setFilters({
      type: 'all',
      priority: 'all',
      status: 'all', 
      tags: [],
      showFavorites: false
    });
    setSearchTerm('');
  };

  const handleNewMarketplace = () => {
    setEditingMarketplace(null);
    setFormOpen(true);
  };

  const handleViewRoutines = (marketplace) => {
    navigate(`/routines?marketplace=${marketplace.id}`);
  };

  const handleCloseForm = () => {
    setFormOpen(false);
    setEditingMarketplace(null);
  };

  if (isLoading && marketplaces.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        <div className="flex">
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          
          <main className="flex-1 p-6 space-y-6">
            {/* Header Skeleton */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <Skeleton className="h-8 w-48 mb-2" />
                <Skeleton className="h-4 w-96" />
              </div>
              <Skeleton className="h-10 w-40" />
            </div>

            {/* Filters Skeleton */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Skeleton className="h-10 flex-1" />
              <div className="flex gap-2">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-10" />
                <Skeleton className="h-10 w-10" />
              </div>
            </div>

            {/* Grid Skeleton */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-64" />
              ))}
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold">Marketplaces</h1>
              <p className="text-muted-foreground">
                Crie e gerencie seus marketplaces com total autonomia
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleNewMarketplace} disabled={isLoading}>
                <Plus className="mr-2 h-4 w-4" />
                Novo Marketplace
              </Button>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Filters */}
          <MarketplaceFilters
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            filters={filters}
            onFiltersChange={setFilters}
            availableTags={availableTags}
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            onClearFilters={handleClearFilters}
          />

          {/* Results count */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Mostrando {filteredMarketplaces.length} de {marketplaces.length} marketplaces
            </p>
            {isLoading && (
              <div className="text-sm text-muted-foreground">Carregando...</div>
            )}
          </div>

          {/* Marketplace Grid/List */}
          {filteredMarketplaces.length > 0 ? (
            <MarketplaceGrid
              marketplaces={filteredMarketplaces}
              onEdit={handleEdit}
              onDuplicate={handleDuplicate}
              onDelete={handleDelete}
              onToggleFavorite={handleToggleFavorite}
              onToggleActive={handleToggleActive}
              onViewRoutines={handleViewRoutines}
            />
          ) : (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                <Plus className="w-12 h-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Nenhum marketplace encontrado</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || Object.values(filters).some(f => f !== 'all' && f !== false && (Array.isArray(f) ? f.length > 0 : true))
                  ? 'Nenhum marketplace corresponde aos filtros aplicados.'
                  : 'Comece criando seu primeiro marketplace.'}
              </p>
              {(!searchTerm && !Object.values(filters).some(f => f !== 'all' && f !== false && (Array.isArray(f) ? f.length > 0 : true))) && (
                <Button onClick={handleNewMarketplace} disabled={isLoading}>
                  <Plus className="mr-2 h-4 w-4" />
                  Criar Primeiro Marketplace
                </Button>
              )}
            </div>
          )}

          {/* Marketplace Form Modal */}
          <MarketplaceForm
            open={formOpen}
            onClose={handleCloseForm}
            marketplace={editingMarketplace}
            onSave={handleSave}
          />
        </main>
      </div>
    </div>
  );
};

export default Marketplaces;

