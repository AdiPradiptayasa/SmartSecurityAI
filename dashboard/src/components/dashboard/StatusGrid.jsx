import { useState, useEffect } from "react";
import { Camera, Database, Bot, Wifi, Bell } from "lucide-react";
import StatusCard from "./StatusCard";
import { SystemService } from "../../services/systemService";

const ICONS = {
  camera: Camera,
  database: Database,
  ai: Bot,
  mqtt: Wifi,
  telegram: Bell,
};

export default function StatusGrid() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    SystemService.status()
      .then((data) => setItems(data.items))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-2xl px-5 py-4">
        Gagal memuat status: {error}
      </div>
    );
  }

  if (!items) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-32 bg-slate-900 border border-slate-800 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
      {items.map((item) => {
        const Icon = ICONS[item.key] || Camera;
        return (
          <StatusCard
            key={item.key}
            title={item.title}
            value={item.value}
            status={item.status}
            icon={<Icon size={22} />}
          />
        );
      })}
    </div>
  );
}