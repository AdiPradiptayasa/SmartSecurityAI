import requests
import time

ESP32CAM_URL_CAPTURE = "http://192.168.137.50"  # port 80 (default, tidak ditulis)

_cache = {"status": False, "last_checked": 0}
CACHE_TTL = 5


def is_camera_online():
    now = time.time()

    if now - _cache["last_checked"] < CACHE_TTL:
        return _cache["status"]

    try:
        response = requests.get(f"{ESP32CAM_URL_CAPTURE}/capture", timeout=1.5)
        online = response.status_code == 200
        print(f"[CAMERA CHECK] Status code: {response.status_code}, online: {online}")
    except requests.exceptions.RequestException as e:
        online = False
        print(f"[CAMERA CHECK] Error: {e}")

    _cache["status"] = online
    _cache["last_checked"] = now
    return online