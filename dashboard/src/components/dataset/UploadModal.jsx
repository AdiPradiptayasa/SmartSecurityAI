import { useState } from "react";
import { X, Upload, Loader2 } from "lucide-react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import { DatasetService } from "../../services/datasetService";
import { showSuccess, showError } from "../../utils/alert";

export default function UploadModal({ isOpen, onClose, onUploaded, defaultName = "" }) {
  const [name, setName] = useState(defaultName);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!name.trim()) {
      showError("Nama kosong", "Masukkan nama orang terlebih dahulu");
      return;
    }
    if (files.length === 0) {
      showError("Belum ada foto", "Pilih minimal 1 foto untuk diupload");
      return;
    }

    setUploading(true);
    try {
      const result = await DatasetService.uploadPhotos(name.trim(), files);
      showSuccess("Upload Berhasil", result.message);
      setFiles([]);
      onUploaded?.();
      onClose();
    } catch (err) {
      showError("Upload Gagal", err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-white">Upload Dataset</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <Input
            label="Nama Orang"
            placeholder="Contoh: Adi Pradipta"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={!!defaultName}
          />

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Pilih Foto (bisa banyak sekaligus)
            </label>
            <input
              type="file"
              accept="image/jpeg,image/png"
              multiple
              onChange={(e) => setFiles(e.target.files)}
              className="w-full text-sm text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700"
            />
            {files.length > 0 && (
              <p className="text-xs text-slate-500 mt-2">{files.length} foto dipilih</p>
            )}
          </div>

          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-3 text-xs text-blue-300">
            Setelah upload, jalankan "Re-run Enrollment" supaya foto baru ini benar-benar dipakai sistem AI.
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button variant="secondary" className="flex-1 justify-center" onClick={onClose} disabled={uploading}>
            Batal
          </Button>
          <Button
            variant="primary"
            className="flex-1 justify-center"
            onClick={handleUpload}
            disabled={uploading}
            icon={uploading ? Loader2 : Upload}
          >
            {uploading ? "Mengupload..." : "Upload"}
          </Button>
        </div>
      </div>
    </div>
  );
}