import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const IdeaDetail = () => {
  const { ideaId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Button variant="ghost" onClick={() => navigate("/dashboard")}>
          ← Back
        </Button>
        <h1 className="text-2xl font-bold text-foreground">Idea: {ideaId}</h1>
        <p className="text-muted-foreground">Detailed view coming soon.</p>
      </div>
    </div>
  );
};

export default IdeaDetail;
