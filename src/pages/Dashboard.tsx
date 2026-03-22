import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Your saved ideas will appear here.</p>
        <Button variant="outline" onClick={() => navigate("/research")}>
          Start New Research
        </Button>
      </div>
    </div>
  );
};

export default Dashboard;
