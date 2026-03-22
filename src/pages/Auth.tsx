import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Auth = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm space-y-6">
        <h1 className="text-2xl font-bold text-center text-foreground">Sign In</h1>
        <Input
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Button className="w-full" onClick={() => navigate("/dashboard")}>
          Continue
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          Or{" "}
          <button className="underline" onClick={() => navigate("/research")}>
            skip to research
          </button>
        </p>
      </div>
    </div>
  );
};

export default Auth;
