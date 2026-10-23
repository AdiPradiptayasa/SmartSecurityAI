import { useState, useEffect, useRef } from "react";
import { User, Clock, MapPin } from "lucide-react";
import SectionCard from "./SectionCard";
import Badge from "../ui/Badge";
import { EventService } from "../../services/eventService";

const API_URL = import.meta.env.VITE_API_URL;
const POLL_INTERVAL_MS = 3000;
const NO_FACE_LABEL = "No Face Detected";

function describe(event) {
  if (!event) {
    return {
      title: "Waiting...",
      subtitle: "Belum ada deteksi",
      badge: { text: "STANDBY", type: "info" },
    };
  }
  if (event.person === NO_FACE_LABEL) {
    return {
      title: "Gerakan Terdeteksi",
      subtitle: "Wajah tidak ditemukan pada citra",
      badge: { text: "NO FACE", type: "warning" },
    };
  }
  if (event.status === "known") {
    return {
      title: event.person,
      subtitle: `Confidence ${event.confidence ?? "-"}%`,
      badge: { text: "OWNER", type: "success" },
    };
  }
  return {
    title: "Orang Tak Dikenal",
    subtitle: `Similarity ${event.confidence ?? "-"}%`,
    badge: { text: "UNKNOWN", type: "danger" },
  };
}

function timeAgo(dateStr, now) {
  if (!dateStr) return "-";
  const diff = Math.max(0, Math.floor((now - new Date(dateStr).getTime()) / 1000));
  if (diff < 5) return "baru saja";
  if (diff < 60) return `${diff} detik lalu`;
  const minutes = Math.floor(diff / 60);
  if (minutes < 60) return `${minutes} menit lalu`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} jam lalu`;
  return `${Math.floor(hours / 24)} hari lalu`;
}

export default function LatestDetection() {
  const [latest, setLatest] = useState(null);
  const [isNew, setIsNew] = useState(false);
  const [imgFailed, setImgFailed] = useState(false);
  const [now, setNow] = useState(Date.now());

  const lastIdRef = useRef(null);
  const initializedRef = useRef(false);
  const flashTimerRef = useRef(null);

  // Polling event terbaru dari backend
  useEffect(() => {
    let cancelled = false;

    const fetchLatest = async () => {
      if (document.hidden) return; // hemat request saat tab tidak aktif
      try {
        const data = await EventService.getAll(1);
        if (cancelled) return;

        const event = data.events?.[0] ?? null;
        const id = event?._id ?? null;

        if (id !== lastIdRef.current) {
          // tandai "baru" hanya untuk event yang masuk setelah halaman terbuka
          if (initializedRef.current && id !== null) {
            setIsNew(true);
            clearTimeout(flashTimerRef.current);
            flashTimerRef.current = setTimeout(() => setIsNew(false), 2500);
          }
          lastIdRef.current = id;
          setImgFailed(false);
          setLatest(event);
        }
        initializedRef.current = true;
      } catch {
        // error sementara diabaikan, data terakhir tetap ditampilkan
      }
    };

    fetchLatest();
    const timer = setInterval(fetchLatest, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(timer);
      clearTimeout(flashTimerRef.current);
    };
  }, []);

  // Tick 1 detik untuk label "x detik lalu"
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  const view = describe(latest);
  const imageUrl = latest?.image_url ? `${API_URL}${latest.image_url}` : null;

  return (
    <SectionCard
      title="Latest Detection"
      action={
        <span className="flex items-center gap-1.5 text-xs text-slate-500">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          Auto-refresh
        </span>
      }
    >
      <div className="flex flex-col items-center">
        <div
          className={`w-full aspect-[4/3] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center transition-all ${
            isNew ? "ring-2 ring-blue-500 animate-pulse" : ""
          }`}
        >
          {imageUrl && !imgFailed ? (
            <img
              src={imageUrl}
              alt="Deteksi terbaru"
              className="w-full h-full object-cover"
              onError={() => setImgFailed(true)}
            />
          ) : (
            <User size={56} className="text-slate-600" strokeWidth={1.5} />
          )}
        </div>

        <h2 className="mt-5 text-xl font-bold text-white text-center">{view.title}</h2>
        <p className="text-slate-400 text-sm text-center">{view.subtitle}</p>

        <div className="mt-4">
          <Badge text={view.badge.text} type={view.badge.type} />
        </div>

        <div className="mt-6 w-full space-y-3 text-sm border-t border-slate-800 pt-4">
          <div className="flex justify-between items-center">
            <span className="text-slate-500 flex items-center gap-1.5">
              <MapPin size={14} />
              Camera
            </span>
            <span className="text-slate-200 font-medium">{latest?.location || "-"}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-500 flex items-center gap-1.5">
              <Clock size={14} />
              Time
            </span>
            <span className="text-slate-200 font-mono">
              {latest ? new Date(latest.created_at).toLocaleTimeString("id-ID") : "--:--:--"}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-500">Terakhir</span>
            <span className="text-slate-400 text-xs">
              {latest ? timeAgo(latest.created_at, now) : "-"}
            </span>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}