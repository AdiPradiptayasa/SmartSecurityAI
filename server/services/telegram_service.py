import threading
import time
import requests

TELEGRAM_BOT_TOKEN = "8822504564:AAEXDfLjRYfClR4DDKz80514EQufss9RV8A"
TELEGRAM_CHAT_ID = "5146559437"

TELEGRAM_SEND_MESSAGE_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
)
TELEGRAM_SEND_PHOTO_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
)
TELEGRAM_GET_ME_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
TELEGRAM_GET_UPDATES_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
)

_telegram_cache = {"status": False, "last_checked": 0}
TELEGRAM_CACHE_TTL = 30
_last_update_id = 0


def send_telegram_message(text):
  try:
    response = requests.post(
        TELEGRAM_SEND_MESSAGE_URL,
        data={
            "chat_id": str(TELEGRAM_CHAT_ID),
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=5,
    )
    if response.status_code == 200:
      print("[TELEGRAM] Pesan teks berhasil terkirim ke pengguna")
    else:
      print(
          f"[TELEGRAM] Gagal kirim teks. Status: {response.status_code},"
          f" Respon: {response.text}"
      )
  except requests.exceptions.RequestException as e:
    print(f"[TELEGRAM] Error send_telegram_message: {e}")


def send_telegram_photo(image_bytes, caption):
  try:
    response = requests.post(
        TELEGRAM_SEND_PHOTO_URL,
        data={
            "chat_id": str(TELEGRAM_CHAT_ID),
            "caption": caption,
            "parse_mode": "HTML",
        },
        files={"photo": ("capture.jpg", image_bytes, "image/jpeg")},
        timeout=10,
    )
    if response.status_code == 200:
      print("[TELEGRAM] Notifikasi foto berhasil terkirim")
    else:
      print(
          f"[TELEGRAM] Gagal kirim foto. Status: {response.status_code},"
          f" Respon: {response.text}"
      )
  except requests.exceptions.RequestException as e:
    print(f"[TELEGRAM] Error send_telegram_photo: {e}")


def notify_detection(image_bytes, person, status, location="Living Room"):
  if status == "known":
    icon, label = "✅", "Owner Terdeteksi"
    name_line = f"👤 Nama: {person}\n"
  elif status == "no_face":
    icon, label = "🔔", "Gerakan Terdeteksi (Wajah Tidak Terbaca)"
    name_line = ""
  else:
    icon, label = "⚠️", "Orang Tak Dikenal Terdeteksi"
    name_line = f"👤 Nama: {person}\n"

  caption = f"{icon} <b>{label}</b>\n\n{name_line}📍 Lokasi: {location}\n"

  if image_bytes:
    send_telegram_photo(image_bytes, caption)
  else:
    send_telegram_message(caption)

def is_telegram_configured():
  now = time.time()
  if now - _telegram_cache["last_checked"] < TELEGRAM_CACHE_TTL:
    return _telegram_cache["status"]

  try:
    response = requests.get(TELEGRAM_GET_ME_URL, timeout=3)
    online = response.status_code == 200 and response.json().get("ok", False)
  except requests.exceptions.RequestException:
    online = False

  _telegram_cache["status"] = online
  _telegram_cache["last_checked"] = now
  return online


# =====================================================
# FORMAT STATUS HEALTH SERVICE UNTUK TELEGRAM
# =====================================================
def format_system_status(health_data):
  # Helper badge untuk boolean / string
  def get_badge(val):
    if val is True or str(val).lower() in ["online", "connected", "running", "ok"]:
      return "🟢 Online"
    return "🔴 Offline"

  cam_st = get_badge(health_data.get("camera", False))
  db_st = get_badge(health_data.get("database", False))
  mqtt_st = get_badge(health_data.get("mqtt", False))
  ai_st = get_badge(health_data.get("ai", False))
  server_st = get_badge(health_data.get("server", "running"))
  version = health_data.get("version", "1.0.0")

  message = (
      "🖥️ <b>STATUS SISTEM & HARDWARE</b>\n"
      "<i>(Sinkron dengan Health Service Web)</i>\n\n"
      f"⚙️ <b>Core Server:</b> {server_st} (v{version})\n"
      f"📷 <b>ESP32-CAM:</b> {cam_st}\n"
      f"🗄️ <b>Basis Data (MongoDB):</b> {db_st}\n"
      f"📡 <b>MQTT Broker:</b> {mqtt_st}\n"
      f"🧠 <b>AI Server (YOLO/Face):</b> {ai_st}\n"
  )
  return message


# =====================================================
# POLLING DAEMON UNTUK PERINTAH BOT
# =====================================================
def _poll_telegram_commands(get_status_func):
  global _last_update_id
  print("[TELEGRAM] Listener /status aktif dan mulai mendengarkan pesan...")

  while True:
    try:
      params = {"offset": _last_update_id + 1, "timeout": 10}
      response = requests.get(
          TELEGRAM_GET_UPDATES_URL, params=params, timeout=15
      )

      if response.status_code == 200:
        data = response.json()
        updates = data.get("result", [])

        for update in updates:
          _last_update_id = update["update_id"]
          message = update.get("message", {})
          text = message.get("text", "").strip().lower()
          chat_id = str(message.get("chat", {}).get("id", ""))

          print(
              f"[TELEGRAM LOG] Diterima: '{text}' dari ID: {chat_id} (Target:"
              f" {TELEGRAM_CHAT_ID})"
          )

          # Cek perintah
          if text in ["/status", "/hardware", "/info", "status", "cek status"]:
            print("[TELEGRAM] Membaca data dari HealthService...")
            try:
              status_info = get_status_func()
              reply_text = format_system_status(status_info)
              send_telegram_message(reply_text)
            except Exception as err:
              print(f"[TELEGRAM] Gagal mengeksekusi get_status_func: {err}")
              send_telegram_message(
                  f"⚠️ Gagal mengambil status sistem: {err}"
              )

    except requests.exceptions.RequestException as e:
      print(f"[TELEGRAM NETWORK] Gagal polling getUpdates: {e}")
    except Exception as ex:
      print(f"[TELEGRAM UNEXPECTED ERROR] {ex}")

    time.sleep(1)


def start_telegram_bot(get_status_func):
  thread = threading.Thread(
      target=_poll_telegram_commands, args=(get_status_func,), daemon=True
  )
  thread.start()