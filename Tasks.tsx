import { useState } from "react";
import { Plus, Filter, Search } from "lucide-react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import TaskCard from "@/components/dashboard/TaskCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Tasks = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const allTasks = [
    {
      id: "1",
      title: "Atualizar preços da categoria Eletrônicos",
      description: "Ajustar preços baseado na análise de concorrência semanal",
      status: "in-progress" as const,
      priority: "high" as const,
      marketplace: "mercado-livre" as const,
      assignee: { name: "Maria Silva", initials: "MS", avatar: "" },
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
      assignee: { name: "João Santos", initials: "JS", avatar: "" },
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
      assignee: { name: "Ana Costa", initials: "AC", avatar: "" },
      dueDate: "Ontem, 18:00",
      category: "SEO"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Gerenciamento de Tarefas</h1>
              <p className="text-muted-foreground">
                Organize e acompanhe todas as suas tarefas de marketplace
              </p>
            </div>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova Tarefa
            </Button>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input placeholder="Buscar tarefas..." className="pl-10" />
                </div>
                <Select>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="todo">A Fazer</SelectItem>
                    <SelectItem value="in-progress">Em Progresso</SelectItem>
                    <SelectItem value="completed">Concluído</SelectItem>
                  </SelectContent>
                </Select>
                <Select>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Marketplace" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="mercado-livre">Mercado Livre</SelectItem>
                    <SelectItem value="shopee">Shopee</SelectItem>
                    <SelectItem value="shein">Shein</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Tasks Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {allTasks.map((task) => (
              <TaskCard key={task.id} {...task} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Tasks;