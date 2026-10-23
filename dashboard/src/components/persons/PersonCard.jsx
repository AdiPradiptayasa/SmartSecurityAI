import { User, Images } from "lucide-react";
import Badge from "../ui/Badge";

export default function PersonCard({ name, role, status, images, lastSeen }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 transition-all duration-300 hover:border-slate-700 hover:-translate-y-1">
      <div className="flex items-start justify-between">
        <div className="w-14 h-14 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
          <User size={26} className="text-slate-500" />
        </div>
        <Badge
          text={status === "registered" ? "Registered" : "Pending"}
          type={status === "registered" ? "success" : "warning"}
        />
      </div>

      <h3 className="mt-4 font-semibold text-white">{name}</h3>
      <p className="text-sm text-slate-500">{role}</p>

      <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
        <span className="flex items-center gap-1.5 text-slate-500">
          <Images size={14} />
          {images} images
        </span>
        <span className="text-slate-500">Seen {lastSeen}</span>
      </div>
    </div>
  );
}