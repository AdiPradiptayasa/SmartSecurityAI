export default function StatCard({ title, value, icon, accent = "blue" }) {
  const colors = {
    blue: "bg-blue-500/10 text-blue-400",
    emerald: "bg-emerald-500/10 text-emerald-400",
    amber: "bg-amber-500/10 text-amber-400",
    red: "bg-red-500/10 text-red-400",
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl px-5 py-4 flex items-center justify-between">
      <div>
        <p className="text-xs text-slate-500">{title}</p>
        <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
      </div>
      <div className={`p-3 rounded-xl ${colors[accent]}`}>{icon}</div>
    </div>
  );
}