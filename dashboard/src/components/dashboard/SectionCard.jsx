export default function SectionCard({ title, action, children }) {
  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden transition-colors duration-300 hover:border-slate-700">
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <h2 className="font-semibold text-white">{title}</h2>
        {action && <div>{action}</div>}
      </div>

      <div className="p-5">{children}</div>
    </div>
  );
}