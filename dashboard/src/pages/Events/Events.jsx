import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, User, Trash2, ZoomIn } from "lucide-react";

import PageTitle from "../../components/ui/PageTitle";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import ImagePreviewModal from "../../components/ui/ImagePreviewModal";
import { EventService } from "../../services/eventService";
import { confirmDelete, showSuccess, showError } from "../../utils/alert";

const API_URL = import.meta.env.VITE_API_URL;
const PAGE_SIZE = 8;

const STATUS_MAP = {
  known: { text: "Owner", type: "success" },
  unknown: { text: "Unknown", type: "warning" },
};

function formatTime(dateStr) {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleString("id-ID", {
    dateStyle: "medium",
    timeStyle: "medium",
  });
}

export default function Events() {
  const [events, setEvents] = useState(null);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [deletingId, setDeletingId] = useState(null);
  const [previewImage, setPreviewImage] = useState(null); // { url, title }

  const loadEvents = () => {
    EventService.getAll(200)
      .then((data) => setEvents(data.events))
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handleDelete = async (eventId) => {
    const result = await confirmDelete({
      title: "Hapus Event Ini?",
      text: "Foto dan data event akan dihapus permanen dan tidak bisa dikembalikan.",
    });

    if (!result.isConfirmed) return;

    setDeletingId(eventId);
    try {
      await EventService.deleteOne(eventId);
      setEvents((prev) => prev.filter((e) => e._id !== eventId));
      showSuccess("Terhapus!", "Event berhasil dihapus.");
    } catch (err) {
      showError("Gagal Menghapus", err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const handleDeleteAll = async () => {
    const result = await confirmDelete({
      title: `Hapus Semua ${events.length} Event?`,
      text: "Semua foto dan data event akan dihapus permanen dan tidak bisa dikembalikan.",
      confirmText: "Ya, Hapus Semua",
    });

    if (!result.isConfirmed) return;

    try {
      await EventService.deleteAll();
      setEvents([]);
      showSuccess("Terhapus!", "Semua event berhasil dihapus.");
    } catch (err) {
      showError("Gagal Menghapus", err.message);
    }
  };

  if (error) return <p className="text-red-400">Gagal memuat: {error}</p>;
  if (!events) return <p className="text-slate-500">Memuat data...</p>;

  const totalPages = Math.max(1, Math.ceil(events.length / PAGE_SIZE));
  const paginated = events.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <PageTitle title="Event Logs" subtitle="Riwayat deteksi wajah dari seluruh kamera" />
        {events.length > 0 && (
          <Button variant="danger" size="sm" icon={Trash2} onClick={handleDeleteAll}>
            Hapus Semua
          </Button>
        )}
      </div>

      {events.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl">
          <p className="text-slate-500">Belum ada event tercatat</p>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-left text-slate-500">
                  <th className="px-5 py-3 font-medium">Foto</th>
                  <th className="px-5 py-3 font-medium">Waktu</th>
                  <th className="px-5 py-3 font-medium">Terdeteksi</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Lokasi</th>
                  <th className="px-5 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {paginated.map((e) => {
                  const statusInfo = STATUS_MAP[e.status] || { text: e.status, type: "info" };

                  return (
                    <tr
                      key={e._id}
                      className="border-b border-slate-800/60 last:border-0 hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="px-5 py-4">
                        {e.image_url ? (
                          <button
                            onClick={() =>
                              setPreviewImage({
                                url: `${API_URL}${e.image_url}`,
                                title: `${e.person} - ${formatTime(e.created_at)}`,
                              })
                            }
                            className="relative group w-14 h-14 rounded-lg overflow-hidden border border-slate-800 hover:border-blue-500 transition-colors"
                          >
                            <img
                              src={`${API_URL}${e.image_url}`}
                              alt="Capture"
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 flex items-center justify-center transition-colors">
                              <ZoomIn size={16} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                          </button>
                        ) : (
                          <div className="w-14 h-14 rounded-lg bg-slate-800 flex items-center justify-center text-slate-600 text-xs">
                            N/A
                          </div>
                        )}
                      </td>
                      <td className="px-5 py-4 text-slate-400 font-mono text-xs">
                        {formatTime(e.created_at)}
                      </td>
                      <td className="px-5 py-4">
                        <span className="flex items-center gap-2 text-slate-200">
                          <User size={14} className="text-slate-500" />
                          {e.person}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <Badge text={statusInfo.text} type={statusInfo.type} />
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-slate-400 text-xs">{e.location || "-"}</span>
                      </td>
                      <td className="px-5 py-4">
                        <button
                          onClick={() => handleDelete(e._id)}
                          disabled={deletingId === e._id}
                          className="text-slate-500 hover:text-red-400 transition-colors disabled:opacity-40"
                          title="Hapus event"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between px-5 py-4 border-t border-slate-800 text-sm text-slate-500">
            <span>
              Halaman {page} dari {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                icon={ChevronLeft}
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Prev
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page === totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ChevronRight size={16} />
              </Button>
            </div>
          </div>
        </div>
      )}

      <ImagePreviewModal
        isOpen={!!previewImage}
        onClose={() => setPreviewImage(null)}
        imageUrl={previewImage?.url}
        title={previewImage?.title}
      />
    </div>
  );
}