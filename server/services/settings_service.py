import json
import os

SETTINGS_PATH = "server/config/app_settings.json"

DEFAULT_SETTINGS = {
    "system_armed": True,          # kalau False, motion terdeteksi tidak diproses sama sekali
    "telegram_enabled": True,      # kirim notifikasi Telegram atau tidak
    "auto_alarm_enabled": True,    # trigger buzzer Wemos saat unknown terdeteksi
}


class SettingsService:

    def __init__(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        if not os.path.exists(SETTINGS_PATH):
            self._save(DEFAULT_SETTINGS)

    def _save(self, settings):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)

    def get_settings(self):
        if not os.path.exists(SETTINGS_PATH):
            self._save(DEFAULT_SETTINGS)
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)

    def update_settings(self, partial_update: dict):
        current = self.get_settings()
        current.update(partial_update)
        self._save(current)
        return current