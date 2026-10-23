import { useState, useEffect } from "react";
import { Save, AlertTriangle } from "lucide-react";

import PageTitle from "../../components/ui/PageTitle";
import SectionCard from "../../components/dashboard/SectionCard";
import Toggle from "../../components/ui/Toggle";
import Button from "../../components/ui/Button";
import { SettingsService } from "../../services/settingsService";
import { showSuccess, showError } from "../../utils/alert";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    SettingsService.get()
      .then(setSettings)
      .catch((err) => showError("Gagal memuat settings", err.message));
  }, []);

  const handleToggle = async (key, value) => {
    const previous = settings;
    setSettings((s) => ({ ...s, [key]: value })); // update optimis di UI

    setSaving(true);
    try {
      await SettingsService.update({ [key]: value });
    } catch (err) {
      setSettings(previous); // rollback kalau gagal
      showError("Gagal menyimpan", err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!settings) return <p className="text-slate-500">Memuat settings...</p>;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <PageTitle title="Settings" subtitle="Konfigurasi sistem monitoring" />
      </div>

      <div className="grid grid-cols-12 gap-5 items-start">
        <div className="col-span-12 lg:col-span-8 space-y-5">
          <SectionCard title="System Control">
            <div className="space-y-4">
              <Toggle
                checked={settings.system_armed}
                onChange={(val) => handleToggle("system_armed", val)}
                label="System Armed"
                description="Kalau nonaktif, deteksi PIR tidak akan diproses sama sekali (mode standby penuh)"
              />
              <Toggle
                checked={settings.auto_alarm_enabled}
                onChange={(val) => handleToggle("auto_alarm_enabled", val)}
                label="Auto Alarm"
                description="Trigger buzzer otomatis saat wajah tak dikenal terdeteksi"
              />
            </div>
          </SectionCard>

          <SectionCard title="Notifications">
            <div className="space-y-4">
              <Toggle
                checked={settings.telegram_enabled}
                onChange={(val) => handleToggle("telegram_enabled", val)}
                label="Telegram Bot"
                description="Kirim notifikasi + foto ke Telegram setiap ada deteksi wajah"
              />
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-4 space-y-5">
          <SectionCard title="System Info">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Status</span>
                <span className={settings.system_armed ? "text-green-400" : "text-amber-400"}>
                  {settings.system_armed ? "Armed" : "Standby"}
                </span>
              </div>
            </div>
          </SectionCard>

          <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-5">
            <div className="flex items-center gap-2 text-red-400 font-semibold mb-2">
              <AlertTriangle size={18} />
              Danger Zone
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Fitur reset database belum tersedia di versi ini.
            </p>
            <Button variant="danger" size="sm" className="w-full justify-center" disabled>
              Reset System
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}