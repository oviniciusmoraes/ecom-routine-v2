import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, CalendarDays, Clock, Plus, Search, Filter, Play, Pause, Edit, Copy, Archive } from "lucide-react";
import { RoutineForm } from "@/components/routines/RoutineForm";
import { RoutineCard } from "@/components/routines/RoutineCard";
import { RoutineCalendar } from "@/components/routines/RoutineCalendar";
import { cn } from "@/lib/utils";

const mockRoutines = [
  {
    id: 1,
    name: "Verificação Diária Shopee Filial",
    description: "Análise diária de métricas e verificação de anormalidades",
    marketplace: "Shopee Filial",
    marketplaceColor: "bg-shopee",
    frequency: "Diária",
    nextExecution: "2024-01-15 09:00",
    responsible: "João Silva",
    status: "active",
    tasks: 3,
    estimatedTime: "45 min"
  },
  {
    id: 2,
    name: "Análise Semanal ML Matriz",
    description: "Comparação de métricas e otimização de anúncios",
    marketplace: "Mercado Livre Matriz",
    marketplaceColor: "bg-mercadolivre",
    frequency: "Semanal - Segunda",
    nextExecution: "2024-01-15 10:00",
    responsible: "Maria Santos",
    status: "active",
    tasks: 5,
    estimatedTime: "2h 30min"
  },
  {
    id: 3,
    name: "Fechamento Mensal Shein",
    description: "Relatórios mensais e análise de performance",
    marketplace: "Shein Filial",
    marketplaceColor: "bg-shein",
    frequency: "Mensal",
    nextExecution: "2024-01-31 16:00",
    responsible: "Carlos Lima",
    status: "paused",
    tasks: 8,
    estimatedTime: "3h 15min"
  }
];

const Routines = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [frequencyFilter, setFrequencyFilter] = useState("all");

  const filteredRoutines = mockRoutines.filter(routine => {
    const matchesSearch = routine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         routine.marketplace.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || routine.status === statusFilter;
    const matchesFrequency = frequencyFilter === "all" || routine.frequency.toLowerCase().includes(frequencyFilter.toLowerCase());
    
    return matchesSearch && matchesStatus && matchesFrequency;
  });

  const stats = {
    totalRoutines: mockRoutines.length,
    activeRoutines: mockRoutines.filter(r => r.status === "active").length,
    todayExecutions: 5,
    completionRate: 94
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <main className="md:ml-64 p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Gestão de Rotinas</h1>
            <p className="text-muted-foreground">Configure e monitore rotinas automatizadas para seus marketplaces</p>
          </div>
          <Button onClick={() => setShowForm(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            Nova Rotina
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Rotinas Ativas</p>
                  <p className="text-3xl font-bold text-primary">{stats.activeRoutines}</p>
                </div>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Play className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Execuções Hoje</p>
                  <p className="text-3xl font-bold text-shopee">{stats.todayExecutions}</p>
                </div>
                <div className="h-12 w-12 rounded-lg bg-shopee/10 flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-shopee" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Taxa de Conclusão</p>
                  <p className="text-3xl font-bold text-success">{stats.completionRate}%</p>
                </div>
                <div className="h-12 w-12 rounded-lg bg-success/10 flex items-center justify-center">
                  <CalendarDays className="h-6 w-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total de Rotinas</p>
                  <p className="text-3xl font-bold text-foreground">{stats.totalRoutines}</p>
                </div>
                <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center">
                  <Clock className="h-6 w-6 text-muted-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar rotinas..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os Status</SelectItem>
                  <SelectItem value="active">Ativo</SelectItem>
                  <SelectItem value="paused">Pausado</SelectItem>
                  <SelectItem value="archived">Arquivado</SelectItem>
                </SelectContent>
              </Select>
              <Select value={frequencyFilter} onValueChange={setFrequencyFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="Frequência" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas as Frequências</SelectItem>
                  <SelectItem value="diária">Diária</SelectItem>
                  <SelectItem value="semanal">Semanal</SelectItem>
                  <SelectItem value="mensal">Mensal</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <Tabs defaultValue="list" className="space-y-6">
          <TabsList className="grid w-full max-w-[400px] grid-cols-2">
            <TabsTrigger value="list">Lista de Rotinas</TabsTrigger>
            <TabsTrigger value="calendar">Calendário</TabsTrigger>
          </TabsList>

          <TabsContent value="list" className="space-y-4">
            {filteredRoutines.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <CalendarDays className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">Nenhuma rotina encontrada</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchTerm || statusFilter !== "all" || frequencyFilter !== "all"
                      ? "Tente ajustar os filtros de busca"
                      : "Comece criando sua primeira rotina automatizada"
                    }
                  </p>
                  {!searchTerm && statusFilter === "all" && frequencyFilter === "all" && (
                    <Button onClick={() => setShowForm(true)} className="gap-2">
                      <Plus className="h-4 w-4" />
                      Criar Primeira Rotina
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {filteredRoutines.map((routine) => (
                  <RoutineCard key={routine.id} routine={routine} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="calendar">
            <RoutineCalendar routines={mockRoutines} />
          </TabsContent>
        </Tabs>
      </main>

      {/* Routine Form Modal */}
      {showForm && (
        <RoutineForm
          open={showForm}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
};

export default Routines;