import { Images, RefreshCw } from "lucide-react";
import Badge from "../ui/Badge";

const STATUS_MAP = {
  ready: { text: "Ready", type: "success" },
  training: { text: "Training", type: "warning" },
  incomplete: { text: "Incomplete", type: "danger" },
};

export default function DatasetCard({ name, images, status, updatedAt }) {
  const s = STATUS_MAP[status];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden transition-all duration-300 hover:border-slate-700 hover:-translate-y-1">
      <div className="h-28 bg-slate-950 flex items-center justify-center border-b border-slate-800">
        <Images size={28} className="text-slate-700" />
      </div>

      <div className="p-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white text-sm">{name}</h3>
          <Badge text={s.text} type={s.type} />
        </div>

        <p className="text-xs text-slate-500 mt-2">{images} images</p>

        <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <RefreshCw size={12} />
            {updatedAt}
          </span>
        </div>
      </div>
    </div>
  );
}