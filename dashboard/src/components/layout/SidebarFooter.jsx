import { useState, useEffect } from "react";
import { HealthService } from "../../services/healthService";

const POLL_INTERVAL = 10000; // cek ulang tiap 10 detik

export default function SidebarFooter({ collapsed }) {
  const [health, setHealth] = useState(null);
  const [backendOnline, setBackendOnline] = useState(true);

  useEffect(() => {
    let timer;

    async function check() {
      try {
        const data = await HealthService.check();
        setHealth(data);
        setBackendOnline(true);
      } catch (err) {
        setBackendOnline(false);
        setHealth(null);
      }
    }

    check();
    timer = setInterval(check, POLL_INTERVAL);

    return () => clearInterval(timer);
  }, []);

  const dbConnected = health?.database ?? false;
  const overallOk = backendOnline && dbConnected;

  if (collapsed) {
    return (
      <div className="p-5 flex justify-center">
        <div
          className={`w-3 h-3 rounded-full ${
            overallOk ? "bg-green-500" : "bg-red-500"
          }`}
        />
      </div>
    );
  }

  return (
    <div className="border-t border-slate-800 p-6">
      <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
        System
      </p>

      <div className="mt-5 space-y-4">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Backend</span>
          <span className={backendOnline ? "text-green-400" : "text-red-400"}>
            {backendOnline ? "Online" : "Offline"}
          </span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-slate-400">MongoDB</span>
          <span className={dbConnected ? "text-green-400" : "text-red-400"}>
            {dbConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>
    </div>
  );
}