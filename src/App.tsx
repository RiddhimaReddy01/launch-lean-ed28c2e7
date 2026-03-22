import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { IdeaProvider } from "@/context/IdeaContext";
import { AuthProvider } from "@/context/AuthContext";
import ErrorBoundary from "@/components/common/ErrorBoundary";
import Landing from "./pages/Landing.tsx";
import Auth from "./pages/Auth.tsx";
import Research from "./pages/Research.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import IdeaDetail from "./pages/IdeaDetail.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <IdeaProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <ErrorBoundary>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/auth" element={<Auth />} />
                <Route path="/research" element={<Research />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/ideas/:ideaId" element={<IdeaDetail />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </ErrorBoundary>
        </TooltipProvider>
      </IdeaProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
