export default function Toggle({ checked, onChange, label, description }) {
  return (
    <div className="flex items-center justify-between py-1">
      {(label || description) && (
        <div>
          {label && <p className="text-sm font-medium text-slate-200">{label}</p>}
          {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
        </div>
      )}

      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`
          relative w-11 h-6 rounded-full transition-colors duration-200 shrink-0
          ${checked ? "bg-blue-600" : "bg-slate-700"}
        `}
      >
        <span
          className={`
            absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full
            transition-transform duration-200
            ${checked ? "translate-x-5" : "translate-x-0"}
          `}
        />
      </button>
    </div>
  );
}