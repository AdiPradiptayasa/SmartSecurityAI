const STATUS_STYLES = {
  success: {
    dot: "bg-emerald-400",
    text: "text-emerald-400",
    iconBg: "bg-emerald-500/10",
    iconText: "text-emerald-400",
    ring: "hover:border-emerald-500/50 hover:shadow-emerald-500/10",
    label: "Operational",
  },
  warning: {
    dot: "bg-amber-400",
    text: "text-amber-400",
    iconBg: "bg-amber-500/10",
    iconText: "text-amber-400",
    ring: "hover:border-amber-500/50 hover:shadow-amber-500/10",
    label: "Warning",
  },
  danger: {
    dot: "bg-red-400",
    text: "text-red-400",
    iconBg: "bg-red-500/10",
    iconText: "text-red-400",
    ring: "hover:border-red-500/50 hover:shadow-red-500/10",
    label: "Disconnected",
  },
  info: {
    dot: "bg-blue-400",
    text: "text-blue-400",
    iconBg: "bg-blue-500/10",
    iconText: "text-blue-400",
    ring: "hover:border-blue-500/50 hover:shadow-blue-500/10",
    label: "Info",
  },
};

export default function StatusCard({ title, value, icon, status = "info" }) {
  const s = STATUS_STYLES[status];

  return (
    <div
      className={`
        group relative overflow-hidden
        bg-slate-900 border border-slate-800 rounded-2xl
        px-6 py-5
        transition-all duration-300
        hover:-translate-y-1 hover:shadow-lg
        ${s.ring}
      `}
    >
      {/* subtle glow accent */}
      <div
        className={`absolute -top-10 -right-10 w-24 h-24 rounded-full blur-3xl opacity-20 ${s.dot}`}
      />

      <div className="relative flex justify-between items-start">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <h2 className="mt-2 text-xl font-semibold text-white">{value}</h2>
        </div>

        <div className={`p-2.5 rounded-xl ${s.iconBg} ${s.iconText}`}>
          {icon}
        </div>
      </div>

      <div className="relative mt-5 flex items-center gap-2">
        <span className="relative flex h-2.5 w-2.5">
          {status === "success" && (
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full ${s.dot} opacity-75`}
            />
          )}
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${s.dot}`} />
        </span>

        <span className={`text-sm font-medium ${s.text}`}>{s.label}</span>
      </div>
    </div>
  );
}