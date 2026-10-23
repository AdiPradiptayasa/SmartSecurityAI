import { X } from "lucide-react";

export default function ImagePreviewModal({ isOpen, onClose, imageUrl, title }) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative max-w-3xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <h3 className="text-sm font-medium text-slate-200">{title || "Preview Foto"}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-2 flex items-center justify-center bg-slate-950">
          <img
            src={imageUrl}
            alt={title || "Preview"}
            className="max-w-full max-h-[70vh] object-contain rounded-lg"
          />
        </div>
      </div>
    </div>
  );
}