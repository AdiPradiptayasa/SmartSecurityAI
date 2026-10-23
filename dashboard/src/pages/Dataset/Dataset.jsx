import { useState, useEffect } from "react";
import { Upload, Database, ImagePlus, CheckCircle2, RefreshCw } from "lucide-react";

import PageTitle from "../../components/ui/PageTitle";
import Button from "../../components/ui/Button";
import StatCard from "../../components/ui/StatCard";
import DatasetCard from "../../components/dataset/DatasetCard";
import UploadModal from "../../components/dataset/UploadModal";
import { DatasetService } from "../../services/datasetService";
import { showSuccess, showError } from "../../utils/alert";

function timeAgo(dateStr) {
  if (!dateStr) return "-";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m lalu`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}j lalu`;
  return `${Math.floor(hours / 24)}h lalu`;
}

export default function Dataset() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [enrolling, setEnrolling] = useState(false);

  const loadData = () => {
    DatasetService.getAll()
      .then(setResult)
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunEnrollment = async () => {
    setEnrolling(true);
    try {
      const res = await DatasetService.runEnrollment();
      if (res.status === "success") {
        showSuccess("Enrollment Selesai", res.message);
        loadData();
      } else {
        showError("Enrollment Gagal", res.message);
      }
    } catch (err) {
      showError("Enrollment Gagal", err.message);
    } finally {
      setEnrolling(false);
    }
  };

  if (error) return <p className="text-red-400">Gagal memuat: {error}</p>;
  if (!result) return <p className="text-slate-500">Memuat data...</p>;

  const { dataset, total_datasets, total_images } = result;
  const readyCount = dataset.filter((d) => d.status === "ready").length;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <PageTitle title="Dataset" subtitle="Kumpulan data wajah untuk training model" />
        <div className="flex gap-3">
          <Button
            variant="secondary"
            icon={enrolling ? RefreshCw : RefreshCw}
            onClick={handleRunEnrollment}
            disabled={enrolling}
          >
            {enrolling ? "Memproses..." : "Re-run Enrollment"}
          </Button>
          <Button icon={Upload} onClick={() => setModalOpen(true)}>
            Upload Dataset
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatCard title="Total Images" value={total_images} icon={<ImagePlus size={20} />} accent="blue" />
        <StatCard title="Ready to Train" value={readyCount} icon={<CheckCircle2 size={20} />} accent="emerald" />
        <StatCard title="Total Dataset" value={total_datasets} icon={<Database size={20} />} accent="amber" />
      </div>

      {dataset.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl">
          <Database className="mx-auto text-slate-700" size={32} />
          <p className="text-slate-500 mt-3">Belum ada dataset tersimpan</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-5">
          {dataset.map((d) => (
            <DatasetCard
              key={d.name}
              name={d.name}
              images={d.images}
              status={d.status}
              updatedAt={timeAgo(d.updated_at)}
            />
          ))}
        </div>
      )}

      <UploadModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onUploaded={loadData}
      />
    </div>
  );
}