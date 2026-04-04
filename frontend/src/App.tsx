import { Activity } from "lucide-react";

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Activity className="w-12 h-12 text-blue-500 animate-pulse" />
        <h1 className="text-3xl font-bold tracking-tight">EchoVault UI is Online</h1>
      </div>
    </div>
  );
}

export default App;