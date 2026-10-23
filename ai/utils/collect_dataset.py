import cv2
import os
import time
import requests
import numpy as np

ESP32CAM_STREAM_URL = "http://192.168.137.50:81/stream"

# Threshold kualitas
BLUR_THRESHOLD = 25      # semakin tinggi = semakin ketat (Laplacian variance)
BRIGHTNESS_MIN = 60       # rata-rata brightness minimum (skala 0-255)
BRIGHTNESS_MAX = 220      # hindari overexposed juga


def get_mjpeg_frame_generator(stream_url):
    response = requests.get(stream_url, stream=True, timeout=10)
    bytes_buffer = bytes()

    for chunk in response.iter_content(chunk_size=1024):
        bytes_buffer += chunk
        start = bytes_buffer.find(b'\xff\xd8')
        end = bytes_buffer.find(b'\xff\xd9')

        if start != -1 and end != -1 and end > start:
            jpg_data = bytes_buffer[start:end + 2]
            bytes_buffer = bytes_buffer[end + 2:]
            frame = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                yield frame


def calculate_blur_score(image):
    """Semakin TINGGI nilainya, semakin TAJAM (fokus) gambarnya"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def calculate_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)


def is_good_quality(face_crop):
    """Cek apakah crop wajah memenuhi standar kualitas"""
    blur_score = calculate_blur_score(face_crop)
    brightness = calculate_brightness(face_crop)

    is_sharp = blur_score >= BLUR_THRESHOLD
    is_bright_enough = BRIGHTNESS_MIN <= brightness <= BRIGHTNESS_MAX

    return is_sharp and is_bright_enough, blur_score, brightness

def crop_with_margin(frame, x, y, w, h, margin=0.25):
    """Crop wajah dengan margin tambahan di sekeliling, supaya tidak terlalu ketat"""
    frame_h, frame_w = frame.shape[:2]

    margin_x = int(w * margin)
    margin_y = int(h * margin)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(frame_w, x + w + margin_x)
    y2 = min(frame_h, y + h + margin_y)

    return frame[y1:y2, x1:x2]

def collect_faces(person_name, dataset_dir="dataset", num_images=50):
    save_dir = os.path.join(dataset_dir, person_name)
    os.makedirs(save_dir, exist_ok=True)

    existing = len(os.listdir(save_dir))
    print(f"[INFO] Sudah ada {existing} foto untuk '{person_name}'")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    print(f"[INFO] Menghubungkan ke ESP32-CAM: {ESP32CAM_STREAM_URL}")
    print(f"[INFO] Mulai capture untuk '{person_name}'. Tekan 'q' untuk berhenti lebih awal.")
    print("[INFO] Foto blur/terlalu gelap/terang OTOMATIS DITOLAK.")
    print("[INFO] Gerakkan kepala perlahan untuk variasi sudut, pastikan area cukup terang.")

    count = 0
    rejected_blur = 0
    rejected_light = 0
    last_capture = 0
    capture_interval = 0.5

    try:
        for frame in get_mjpeg_frame_generator(ESP32CAM_STREAM_URL):
            if count >= num_images:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            display_frame = frame.copy()

            for (x, y, w, h) in faces:
                now = time.time()

                if now - last_capture > capture_interval:
                    face_crop = crop_with_margin(frame, x, y, w, h, margin=0.25)
                    good_quality, blur_score, brightness = is_good_quality(face_crop)

                    box_color = (0, 255, 0) if good_quality else (0, 0, 255)
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), box_color, 2)

                    

                    if good_quality:
                        filename = os.path.join(save_dir, f"{person_name}_{existing + count}.jpg")
                        cv2.imwrite(filename, face_crop)
                        count += 1
                        last_capture = now
                        print(f"[CAPTURE] {count}/{num_images} tersimpan (blur={blur_score:.0f}, brightness={brightness:.0f})")
                    else:
                        if blur_score < BLUR_THRESHOLD:
                            rejected_blur += 1
                        if not (BRIGHTNESS_MIN <= brightness <= BRIGHTNESS_MAX):
                            rejected_light += 1
                else:
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            status_text = f"Captured: {count}/{num_images} | Ditolak: blur={rejected_blur}, cahaya={rejected_light}"
            cv2.putText(display_frame, status_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("Dataset Collection dari ESP32-CAM (Hijau=OK, Merah=Ditolak) - Q untuk keluar", display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gagal konek ke ESP32-CAM: {e}")
    finally:
        cv2.destroyAllWindows()

    print(f"\n[DONE] Total {count} foto BERKUALITAS tersimpan untuk '{person_name}'")
    print(f"[INFO] Ditolak karena blur: {rejected_blur} | Ditolak karena pencahayaan: {rejected_light}")


if __name__ == "__main__":
    name = input("Nama orang (contoh: 'Adi Pradipta' atau 'Unknown_1'): ")
    jumlah = int(input("Jumlah foto BERKUALITAS yang mau diambil (rekomendasi minimal 80): "))
    collect_faces(person_name=name, num_images=jumlah)