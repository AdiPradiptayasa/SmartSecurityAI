import paho.mqtt.client as mqtt
import requests
import cv2
import numpy as np
import os
import sys
import time
import csv
import threading
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ai", "face"))
from classify import FaceClassifier

from server.services.database_service import DatabaseService
from server.services.telegram_service import notify_detection
from server.services.settings_service import SettingsService

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

MOTION_TOPIC = "security/motion"
ALARM_TOPIC = "security/alarm"

ESP32CAM_URL = "http://192.168.137.50"

EVENTS_UPLOAD_DIR = "server/uploads/events"
LOG_DIR = "server/logs"
LATENCY_LOG = os.path.join(LOG_DIR, "latency.csv")
os.makedirs(EVENTS_UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- Parameter burst ---
BURST_FRAMES = 3            # jumlah frame per kejadian PIR
BURST_INTERVAL = 0.3        # jeda antar frame (detik)
MIN_KNOWN_VOTES = 2         # known dari >=2 frame, kecuali tidak ada frame unknown yang bertentangan

# True  : gerakan tanpa wajah terbaca TETAP dikirim ke Telegram (tanpa alarm buzzer)
# False : perilaku lama (diam, dianggap false trigger)
NOTIFY_ON_NO_FACE = True
NO_FACE_LABEL = "Gerakan terdeteksi (wajah tidak terbaca)"

database = DatabaseService()
settings_service = SettingsService()
http = requests.Session()   # keep-alive ke ESP32-CAM

mqtt_connected = False
ai_ready = False
_busy = threading.Lock()    # cegah pemrosesan tumpang tindih

print("[AI] Memuat model deteksi & pengenalan wajah...")
try:
    classifier = FaceClassifier()
    # warm-up: percobaan pertama selalu paling lambat
    classifier.classify_image(np.zeros((480, 640, 3), dtype=np.uint8))
    ai_ready = True
    print("[AI] Model siap digunakan")
except Exception as e:
    print(f"[AI ERROR] Gagal load model: {e}")
    classifier = None
    ai_ready = False


def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print(f"[MQTT] Connected with result code {rc}")
    mqtt_connected = (rc == 0)
    client.subscribe(MOTION_TOPIC)


def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print(f"[MQTT] Disconnected, rc={rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] Pesan dari {msg.topic}: {payload}")

    if msg.topic == MOTION_TOPIC and payload == "motion_detected":
        handle_motion_detected(client)
    elif msg.topic == MOTION_TOPIC and payload == "no_motion":
        print("[INFO] Kondisi kembali normal")


# ---------------------------------------------------------------- capture ---

def capture_frame():
    """Ambil 1 frame dari ESP32-CAM. Return (jpeg_bytes, image_bgr) atau None bila gagal/korup."""
    try:
        response = http.get(f"{ESP32CAM_URL}/capture", timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] Gagal ambil capture dari ESP32-CAM: {e}")
        return None

    if response.status_code != 200 or len(response.content) < 1000:
        print(f"[WARNING] Respons capture tidak valid (status={response.status_code}, {len(response.content)} byte)")
        return None

    image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        print("[WARNING] JPEG korup/terpotong, frame dibuang")
        return None
    return response.content, image


def save_frame(image_bytes):
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    with open(os.path.join(EVENTS_UPLOAD_DIR, filename), "wb") as f:
        f.write(image_bytes)
    return f"/uploads/events/{filename}"


# --------------------------------------------------------------- keputusan ---

def pick_result(entries):
    """Gabungkan hasil beberapa frame jadi satu keputusan.
    Return (entry_terbaik, status) dengan status: known | unknown | no_face."""
    def best(lst):
        return max(lst, key=lambda e: e["cls"]["confidence"])

    known = [e for e in entries if e["cls"] and e["cls"]["status"] == "known"]
    unknown = [e for e in entries if e["cls"] and e["cls"]["status"] == "unknown"]

    if known and len(known) >= len(unknown) and (len(known) >= MIN_KNOWN_VOTES or not unknown):
        return best(known), "known"
    if unknown:
        return best(unknown), "unknown"

    failed = [e for e in entries if e["cls"] and e["cls"]["status"] == "embedding_failed"]
    return (failed[0] if failed else entries[0]), "no_face"


def log_latency(row):
    new_file = not os.path.exists(LATENCY_LOG)
    with open(LATENCY_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "outcome", "person", "confidence", "frames",
                        "capture_s", "ai_s", "notify_s", "total_s"])
        w.writerow(row)


# ------------------------------------------------------------------ alur ----

def process_motion(client):
    t0 = time.time()

    # 1) Ambil burst frame dulu (cepat), baru proses AI
    frames = []
    for i in range(BURST_FRAMES):
        frame = capture_frame()
        if frame:
            frames.append(frame)
        if i < BURST_FRAMES - 1:
            time.sleep(BURST_INTERVAL)
    t_capture = time.time()

    if not frames:
        print("[WARNING] Tidak ada frame valid dari ESP32-CAM, kejadian dilewati")
        log_latency([datetime.now().isoformat(), "capture_failed", "", 0, 0,
                     round(t_capture - t0, 2), 0, 0, round(time.time() - t0, 2)])
        return

    # 2) Klasifikasi tiap frame
    entries = []
    for image_bytes, image in frames:
        cls = None
        if classifier is not None:
            try:
                cls = classifier.classify_image(image)
                print(f"[AI] Hasil klasifikasi: {cls}")
            except Exception as e:
                print(f"[AI ERROR] Gagal menjalankan klasifikasi: {e}")
        entries.append({"bytes": image_bytes, "cls": cls})
    t_ai = time.time()

    # 3) Keputusan
    entry, status = pick_result(entries)
    image_url = save_frame(entry["bytes"])
    t_notify = t_ai

    if status in ("known", "unknown"):
        person = entry["cls"]["person"]
        confidence = entry["cls"]["confidence"]
        print(f"[INFO] Keputusan dari {len(entries)} frame: {person} ({status}, {confidence}%)")

        database.save_event(person=person, status=status, confidence=confidence, image_url=image_url)

        if status == "unknown":
            client.publish(ALARM_TOPIC, "unknown_detected")
            print("[ALARM] Trigger alarm dikirim ke Wemos")

        notify_detection(image_bytes=entry["bytes"], person=person, status=status)
        t_notify = time.time()
    else:
        person, confidence = "No Face Detected", 0.0
        print("[INFO] Wajah tidak terbaca pada semua frame")
        database.save_event(person=person, status="unknown", confidence=0.0, image_url=image_url)

        if NOTIFY_ON_NO_FACE:
            # Tanpa alarm buzzer: hanya info + foto agar pengguna bisa menilai sendiri
            notify_detection(image_bytes=entry["bytes"], person=NO_FACE_LABEL, status="unknown")
            t_notify = time.time()

    log_latency([datetime.now().isoformat(), status, person, confidence, len(entries),
                 round(t_capture - t0, 2), round(t_ai - t_capture, 2),
                 round(t_notify - t_ai, 2), round(time.time() - t0, 2)])
    print(f"[TIMING] capture={t_capture - t0:.2f}s ai={t_ai - t_capture:.2f}s total={time.time() - t0:.2f}s")


def _worker(client):
    try:
        process_motion(client)
    except Exception as e:
        print(f"[ERROR] Gagal memproses kejadian: {e}")
    finally:
        _busy.release()


def handle_motion_detected(client):
    settings = settings_service.get_settings()

    if not settings.get("system_armed", True):
        print("[INFO] Sistem sedang di-nonaktifkan (system_armed=False), motion diabaikan")
        return

    # Jangan blokir loop MQTT; trigger baru saat masih memproses diabaikan
    if not _busy.acquire(blocking=False):
        print("[INFO] Masih memproses kejadian sebelumnya, trigger ini dilewati")
        return

    print("[EVENT] Motion terdeteksi, memproses burst frame...")
    threading.Thread(target=_worker, args=(client,), daemon=True).start()


def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client


def is_mqtt_connected():
    return mqtt_connected


def is_ai_ready():
    return ai_ready
