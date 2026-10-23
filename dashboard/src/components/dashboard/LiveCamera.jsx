import { useState } from "react";
import { VideoOff, Play, Square } from "lucide-react";
import SectionCard from "./SectionCard";
import Badge from "../ui/Badge";
import Button from "../ui/Button";

const ESP32CAM_URL = import.meta.env.VITE_ESP32CAM_URL;

export default function LiveCamera() {
  const [isLive, setIsLive] = useState(false);
  const [streamError, setStreamError] = useState(false);

  const toggleLive = () => {
    setStreamError(false);
    setIsLive((prev) => !prev);
  };

  return (
    <SectionCard
      title="Live Monitoring"
      action={
        isLive && (
          <span className="flex items-center gap-1.5 text-xs text-slate-500">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                streamError ? "bg-slate-600" : "bg-red-500 animate-pulse"
              }`}
            />
            {streamError ? "OFFLINE" : "LIVE"}
          </span>
        )
      }
    >
      <div className="space-y-5">
        <div className="relative bg-slate-950 border border-slate-800 rounded-xl h-[430px] flex items-center justify-center overflow-hidden">
          {!isLive ? (
            <div className="text-center">
              <VideoOff className="mx-auto text-slate-600" size={40} strokeWidth={1.5} />
              <h2 className="text-slate-400 text-xl mt-3">Live View Nonaktif</h2>
              <p className="text-slate-500 mt-1 text-sm mb-5">
                Klik tombol di bawah untuk mulai menonton
              </p>
              <Button icon={Play} onClick={toggleLive}>
                Mulai Live Monitoring
              </Button>
            </div>
          ) : streamError ? (
            <div className="text-center">
              <VideoOff className="mx-auto text-slate-600" size={40} strokeWidth={1.5} />
              <h2 className="text-slate-400 text-xl mt-3">Stream Tidak Tersedia</h2>
              <p className="text-slate-500 mt-1 text-sm">Pastikan ESP32-CAM menyala</p>
            </div>
          ) : (
            <img
              src={`${ESP32CAM_URL}/stream`}
              alt="ESP32-CAM Live Stream"
              className="w-full h-full object-contain"
              onError={() => setStreamError(true)}
            />
          )}
        </div>

        <div className="flex items-center justify-between gap-3">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 flex-1">
            <Badge text="640x480" type="info" />
            <Badge text={isLive && !streamError ? "Online" : "Standby"} type={isLive && !streamError ? "success" : "warning"} />
          </div>

          {isLive && (
            <Button variant="danger" size="sm" icon={Square} onClick={toggleLive}>
              Stop
            </Button>
          )}
        </div>
      </div>
    </SectionCard>
  );
}