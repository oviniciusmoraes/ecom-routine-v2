import { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Calendar, Clock, Play, Pause, CheckCircle, AlertCircle, RotateCcw, ChevronDown, ChevronRight, Plus } from "lucide-react";
import { DailyTaskCard } from "@/components/tasks/DailyTaskCard";
import { WeeklySection } from "@/components/tasks/WeeklySection";
import { MonthlySection } from "@/components/tasks/MonthlySection";
import { cn } from "@/lib/utils";

export type TaskStatus = "not_started" | "in_progress" | "completed" | "overdue";

export interface Task {
  id: string;
  title: string;
  description: string;
  marketplace: string;
  marketplaceColor: string;
  estimatedTime: number; // in minutes
  urls?: string[];
  status: TaskStatus;
  startedAt?: Date;
  completedAt?: Date;
  priority: "low" | "medium" | "high" | "critical";
}

const mockDailyTasks: Task[] = [
  {
    id: "1",
    title: "Verificar página inicial Shopee - anormalidades",
    description: "Análise de picos anômalos de pedidos e verificação geral",
    marketplace: "Shopee Filial",
    marketplaceColor: "bg-shopee",
    estimatedTime: 10,
    urls: ["https://seller.shopee.com.br/"],
    status: "not_started",
    priority: "high"
  },
  {
    id: "2", 
    title: "Analisar métricas de saúde da conta",
    description: "Verificar indicadores e garantir que estão em verde",
    marketplace: "Shopee Filial",
    marketplaceColor: "bg-shopee",
    estimatedTime: 15,
    urls: ["https://seller.shopee.com.br/portal/accounthealth/home"],
    status: "in_progress",
    startedAt: new Date(),
    priority: "high"
  },
  {
    id: "3",
    title: "Tratar pedidos atrasados",
    description: "Resolver pendências e garantir zero atrasos",
    marketplace: "Shopee Filial", 
    marketplaceColor: "bg-shopee",
    estimatedTime: 20,
    urls: ["https://seller.shopee.com.br/portal/accounthealth/issues"],
    status: "not_started",
    priority: "critical"
  },
  {
    id: "4",
    title: "Backup de dados diário",
    description: "Backup automático dos dados importantes",
    marketplace: "Geral",
    marketplaceColor: "bg-muted",
    estimatedTime: 5,
    status: "completed",
    completedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    priority: "medium"
  },
  {
    id: "5",
    title: "Relatório de vendas do dia anterior",
    description: "Compilar e analisar dados de vendas",
    marketplace: "Mercado Livre Matriz",
    marketplaceColor: "bg-mercadolivre", 
    estimatedTime: 30,
    status: "not_started",
    priority: "medium"
  }
];

const DailyTasks = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [tasks, setTasks] = useState<Task[]>(mockDailyTasks);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const updateTaskStatus = (taskId: string, status: TaskStatus) => {
    setTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const updates: Partial<Task> = { status };
        if (status === "in_progress" && task.status !== "in_progress") {
          updates.startedAt = new Date();
        } else if (status === "completed") {
          updates.completedAt = new Date();
        }
        return { ...task, ...updates };
      }
      return task;
    }));
  };

  const resetDailyTasks = () => {
    setTasks(prev => prev.map(task => ({
      ...task,
      status: "not_started" as TaskStatus,
      startedAt: undefined,
      completedAt: undefined
    })));
  };

  const completedTasks = tasks.filter(t => t.status === "completed").length;
  const totalTasks = tasks.length;
  const progressPercentage = (completedTasks / totalTasks) * 100;
  const totalEstimatedTime = tasks
    .filter(t => t.status !== "completed")
    .reduce((sum, task) => sum + task.estimatedTime, 0);

  const getTasksByStatus = (status: TaskStatus) => 
    tasks.filter(task => task.status === status);

  const notStartedTasks = getTasksByStatus("not_started");
  const inProgressTasks = getTasksByStatus("in_progress");
  const completedTasksList = getTasksByStatus("completed");

  return (
    <div className="min-h-screen bg-background">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <main className="md:ml-64 p-6 space-y-6">
        {/* Header with Controls */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-card p-6 rounded-lg border shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 flex-1">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
                  <RotateCcw className="h-5 w-5" />
                  Iniciar Novo Dia
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Iniciar Novo Dia</AlertDialogTitle>
                  <AlertDialogDescription>
                    Todas as rotinas diárias serão resetadas para status "Não Iniciada". 
                    Deseja continuar?
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                  <AlertDialogAction onClick={resetDailyTasks}>
                    Confirmar Reset
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <div className="flex flex-col sm:flex-row gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-success" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Progresso Diário</p>
                      <p className="text-2xl font-bold text-foreground">{Math.round(progressPercentage)}%</p>
                    </div>
                  </div>
                  <Progress value={progressPercentage} className="mt-2" />
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-warning" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Tempo Restante</p>
                      <p className="text-2xl font-bold text-foreground">{totalEstimatedTime}min</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                      <p className="text-2xl font-bold text-foreground">{totalTasks - completedTasks}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="text-right">
            <p className="text-sm text-muted-foreground">
              {currentTime.toLocaleDateString('pt-BR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
            <p className="text-lg font-semibold text-foreground">
              {currentTime.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </p>
          </div>
        </div>

        {/* Daily Tasks Section - Always Expanded */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="h-6 w-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Tarefas Diárias</h2>
              <Badge variant="secondary">{notStartedTasks.length + inProgressTasks.length} pendentes</Badge>
            </div>
          </div>

          {/* Next Tasks */}
          {notStartedTasks.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Play className="h-5 w-5 text-primary" />
                Próximas Tarefas
                <Badge variant="outline">{notStartedTasks.length}</Badge>
              </h3>
              <div className="space-y-3">
                {notStartedTasks.map(task => (
                  <DailyTaskCard 
                    key={task.id} 
                    task={task} 
                    onStatusChange={updateTaskStatus}
                  />
                ))}
              </div>
            </div>
          )}

          {/* In Progress */}
          {inProgressTasks.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Clock className="h-5 w-5 text-warning" />
                Em Andamento
                <Badge variant="secondary">{inProgressTasks.length}</Badge>
              </h3>
              <div className="space-y-3">
                {inProgressTasks.map(task => (
                  <DailyTaskCard 
                    key={task.id} 
                    task={task} 
                    onStatusChange={updateTaskStatus}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed Today */}
          {completedTasksList.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-success" />
                Concluídas Hoje
                <Badge variant="secondary" className="bg-success/10 text-success">
                  {completedTasksList.length}
                </Badge>
              </h3>
              <div className="space-y-3">
                {completedTasksList.map(task => (
                  <DailyTaskCard 
                    key={task.id} 
                    task={task} 
                    onStatusChange={updateTaskStatus}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Weekly Tasks Section */}
        <WeeklySection />

        {/* Monthly Tasks Section */}
        <MonthlySection />
      </main>
    </div>
  );
};

export default DailyTasks;