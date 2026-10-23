import { useState } from "react";
import { VideoOff, Play, Square, RotateCw, Wifi, Gauge } from "lucide-react";

import PageTitle from "../../components/ui/PageTitle";
import SectionCard from "../../components/dashboard/SectionCard";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";

const ESP32CAM_URL = import.meta.env.VITE_ESP32CAM_URL;

export default function Camera() {
  const [isLive, setIsLive] = useState(false);
  const [streamKey, setStreamKey] = useState(0);
  const [streamError, setStreamError] = useState(false);

  const startLive = () => {
    setStreamError(false);
    setStreamKey((k) => k + 1);
    setIsLive(true);
  };

  const stopLive = () => {
    setIsLive(false);
    setStreamError(false);
  };

  const handleReconnect = () => {
    setStreamError(false);
    setStreamKey((k) => k + 1);
  };

  return (
    <div className="space-y-8">
      <PageTitle title="Live Camera" subtitle="ESP32-CAM real-time stream & control" />

      <div className="grid grid-cols-12 gap-5 items-start">
        <div className="col-span-12 lg:col-span-8">
          <SectionCard
            title="Camera Feed"
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
              <div className="relative bg-slate-950 border border-slate-800 rounded-xl h-[480px] flex items-center justify-center overflow-hidden">
                {!isLive ? (
                  <div className="text-center">
                    <VideoOff className="mx-auto text-slate-600" size={44} strokeWidth={1.5} />
                    <h2 className="text-slate-400 text-xl mt-3">Live View Nonaktif</h2>
                    <p className="text-slate-500 mt-1 text-sm mb-5">
                      Klik "Mulai Streaming" untuk melihat kamera secara langsung
                    </p>
                    <Button icon={Play} onClick={startLive}>
                      Mulai Streaming
                    </Button>
                  </div>
                ) : streamError ? (
                  <div className="text-center">
                    <VideoOff className="mx-auto text-slate-600" size={44} strokeWidth={1.5} />
                    <h2 className="text-slate-400 text-xl mt-3">Stream Tidak Tersedia</h2>
                    <p className="text-slate-500 mt-1 text-sm">
                      Pastikan ESP32-CAM menyala dan terhubung ke jaringan
                    </p>
                  </div>
                ) : (
                  <img
                    key={streamKey}
                    src={`${ESP32CAM_URL}/stream`}
                    alt="ESP32-CAM Live Stream"
                    className="w-full h-full object-contain"
                    onError={() => setStreamError(true)}
                  />
                )}
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap gap-3">
                  <Badge text="640x480" type="info" />
                  <Badge
                    text={!isLive ? "Standby" : streamError ? "Offline" : "Streaming"}
                    type={!isLive ? "warning" : streamError ? "danger" : "success"}
                  />
                </div>

                <div className="flex gap-3">
                  {isLive && (
                    <Button variant="secondary" size="sm" icon={RotateCw} onClick={handleReconnect}>
                      Reconnect
                    </Button>
                  )}

                  {isLive ? (
                    <Button variant="danger" size="sm" icon={Square} onClick={stopLive}>
                      Stop Streaming
                    </Button>
                  ) : (
                    <Button variant="primary" size="sm" icon={Play} onClick={startLive}>
                      Mulai Streaming
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-4 space-y-5">
          <SectionCard title="Device Info">
            <div className="space-y-3 text-sm">
              <InfoRow icon={Wifi} label="IP Address" value={ESP32CAM_URL?.replace("http://", "").split(":")[0] || "-"} />
              <InfoRow icon={Gauge} label="Resolution" value="640x480" />
            </div>
          </SectionCard>

          <div className="bg-blue-500/5 border border-blue-500/20 rounded-2xl p-5">
            <p className="text-xs text-slate-400 leading-relaxed">
              <span className="text-blue-400 font-semibold">Info:</span> Deteksi gerakan (PIR sensor)
              dan pencatatan Event Logs tetap berjalan otomatis meskipun live streaming
              dimatikan — kamera hanya mengambil foto snapshot saat ada trigger, terpisah
              dari fitur live view ini.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-2 text-slate-500">
        <Icon size={14} />
        {label}
      </span>
      <span className="text-slate-200 font-medium font-mono">{value}</span>
    </div>
  );
}