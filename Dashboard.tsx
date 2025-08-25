import { useState } from "react";
import { 
  CheckSquare, 
  Clock, 
  TrendingUp, 
  Users, 
  Plus,
  Filter,
  Calendar as CalendarIcon,
  ArrowRight
} from "lucide-react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import StatsCard from "@/components/dashboard/StatsCard";
import TaskCard from "@/components/dashboard/TaskCard";
import MarketplaceOverview from "@/components/dashboard/MarketplaceOverview";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Mock data for tasks
const recentTasks = [
  {
    id: "1",
    title: "Atualizar preços da categoria Eletrônicos",
    description: "Ajustar preços baseado na análise de concorrência semanal",
    status: "in-progress" as const,
    priority: "high" as const,
    marketplace: "mercado-livre" as const,
    assignee: {
      name: "Maria Silva",
      initials: "MS",
      avatar: ""
    },
    dueDate: "Hoje, 15:00",
    category: "Precificação"
  },
  {
    id: "2", 
    title: "Backup semanal dos dados de produtos",
    description: "Rotina automatizada de backup programada para toda quarta-feira",
    status: "todo" as const,
    priority: "medium" as const,
    marketplace: "shopee" as const,
    assignee: {
      name: "João Santos",
      initials: "JS",
      avatar: ""
    },
    dueDate: "Amanhã, 09:00",
    category: "Manutenção"
  },
  {
    id: "3",
    title: "Otimizar títulos dos produtos em alta",
    description: "Implementar palavras-chave trending identificadas pela IA",
    status: "overdue" as const,
    priority: "critical" as const,
    marketplace: "shein" as const,
    assignee: {
      name: "Ana Costa",
      initials: "AC",
      avatar: ""
    },
    dueDate: "Ontem, 18:00",
    category: "SEO"
  },
  {
    id: "4",
    title: "Relatório mensal de performance",
    description: "Consolidar métricas de vendas e produtividade da equipe",
    status: "completed" as const,
    priority: "medium" as const,
    marketplace: "amazon" as const,
    assignee: {
      name: "Carlos Lima",
      initials: "CL",
      avatar: ""
    },
    dueDate: "Concluído",
    category: "Relatórios"
  }
];

const upcomingRoutines = [
  {
    title: "Análise de Tendências Semanais",
    time: "Quinta-feira, 14:00",
    marketplace: "Todos",
    type: "Semanal"
  },
  {
    title: "Atualização de Estoque",
    time: "Sexta-feira, 09:00", 
    marketplace: "Mercado Livre",
    type: "Diária"
  },
  {
    title: "Backup de Segurança",
    time: "Sábado, 02:00",
    marketplace: "Todos",
    type: "Semanal"
  }
];

const Dashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
        />
        
        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6 md:ml-0">
          {/* Welcome Section */}
          <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-foreground">
              Bem-vindo de volta! 👋
            </h1>
            <p className="text-muted-foreground mt-1">
              Aqui está um resumo das suas atividades e marketplaces hoje.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Tarefas Pendentes"
              value="12"
              change="-3 desde ontem"
              changeType="decrease"
              icon={CheckSquare}
              variant="info"
            />
            <StatsCard
              title="Rotinas Ativas"
              value="8"
              change="+2 esta semana"
              changeType="increase" 
              icon={Clock}
              variant="default"
            />
            <StatsCard
              title="Performance da Equipe"
              value="94%"
              change="+5% este mês"
              changeType="increase"
              icon={TrendingUp}
              variant="success"
            />
            <StatsCard
              title="Membros Online"
              value="6/8"
              change="Todos presentes"
              changeType="neutral"
              icon={Users}
              variant="default"
            />
          </div>

          {/* Main Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Recent Tasks */}
            <div className="lg:col-span-2">
              <Card className="animate-slide-up shadow-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <CheckSquare className="h-5 w-5" />
                      Tarefas Recentes
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                      <Select defaultValue="all">
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Todas</SelectItem>
                          <SelectItem value="pending">Pendentes</SelectItem>
                          <SelectItem value="completed">Concluídas</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button size="sm">
                        <Plus className="h-4 w-4 mr-1" />
                        Nova Tarefa
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentTasks.map((task) => (
                      <TaskCard key={task.id} {...task} />
                    ))}
                  </div>
                  <div className="mt-4 text-center">
                    <Button variant="ghost" className="w-full">
                      Ver Todas as Tarefas
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Upcoming Routines */}
            <div>
              <Card className="animate-slide-up shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CalendarIcon className="h-5 w-5" />
                    Próximas Rotinas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {upcomingRoutines.map((routine, index) => (
                      <div 
                        key={index}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card hover:shadow-sm transition-all"
                      >
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{routine.title}</h4>
                          <p className="text-xs text-muted-foreground">{routine.time}</p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className="text-xs">
                            {routine.type}
                          </Badge>
                          <p className="text-xs text-muted-foreground mt-1">
                            {routine.marketplace}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button variant="ghost" className="w-full mt-4">
                    Ver Calendário Completo
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Marketplace Overview */}
          <MarketplaceOverview />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;