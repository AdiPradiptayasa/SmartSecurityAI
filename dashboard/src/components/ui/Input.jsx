export default function Input({ label, hint, className = "", ...props }) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-slate-300 mb-1.5">
          {label}
        </label>
      )}

      <input
        className="
          w-full bg-slate-950 border border-slate-800 rounded-xl
          px-4 py-2.5 text-sm text-white placeholder:text-slate-600
          focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50
          transition-all
        "
        {...props}
      />

      {hint && <p className="text-xs text-slate-500 mt-1.5">{hint}</p>}
    </div>
  );
}