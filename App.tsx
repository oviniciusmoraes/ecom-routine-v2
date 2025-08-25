import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LazyWrapper } from "@/components/ui/lazy-wrapper";

// Lazy load pages for better performance
const Index = lazy(() => import("./pages/Index"));
const DailyTasks = lazy(() => import("./pages/DailyTasks"));
const Marketplaces = lazy(() => import("./pages/Marketplaces"));
const Routines = lazy(() => import("./pages/Routines"));
const NotFound = lazy(() => import("./pages/NotFound"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <LazyWrapper>
                  <Index />
                </LazyWrapper>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/tasks" 
            element={
              <ProtectedRoute>
                <LazyWrapper>
                  <DailyTasks />
                </LazyWrapper>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/marketplaces" 
            element={
              <ProtectedRoute>
                <LazyWrapper>
                  <Marketplaces />
                </LazyWrapper>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/routines" 
            element={
              <ProtectedRoute>
                <LazyWrapper>
                  <Routines />
                </LazyWrapper>
              </ProtectedRoute>
            } 
          />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route 
            path="*" 
            element={
              <LazyWrapper>
                <NotFound />
              </LazyWrapper>
            } 
          />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
