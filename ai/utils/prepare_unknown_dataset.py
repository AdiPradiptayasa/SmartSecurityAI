import cv2
import os
import glob
import random

SOURCE_DIR = "ai/temp_download/lfw-deepfunneled/lfw-deepfunneled"
OUTPUT_DIR = "dataset/Unknown"
TARGET_COUNT = 150  # jumlah total foto "Unknown" yang mau dipakai

# Simulasi kualitas ESP32-CAM
TARGET_SIZE = (160, 160)   # ukuran crop wajah tipikal
JPEG_QUALITY = 30          # kompresi tinggi, meniru kualitas ESP32-CAM


def degrade_quality(image):
    """Simulasikan kualitas gambar ESP32-CAM: resolusi rendah + kompresi JPEG tinggi + sedikit blur"""
    small = cv2.resize(image, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(small, (3, 3), 0)

    encode_param = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
    result, encimg = cv2.imencode('.jpg', blurred, encode_param)
    degraded = cv2.imdecode(encimg, cv2.IMREAD_COLOR)

    return degraded


def prepare_unknown_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_images = glob.glob(os.path.join(SOURCE_DIR, "**", "*.jpg"), recursive=True)
    print(f"[INFO] Ditemukan {len(all_images)} gambar sumber")

    if len(all_images) == 0:
        print("[ERROR] Tidak ada gambar ditemukan. Cek SOURCE_DIR sudah benar.")
        return

    random.shuffle(all_images)
    selected = all_images[:TARGET_COUNT]

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    saved = 0
    for idx, img_path in enumerate(selected):
        image = cv2.imread(img_path)
        if image is None:
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            continue

        x, y, w, h = faces[0]
        face_crop = image[y:y+h, x:x+w]

        degraded = degrade_quality(face_crop)

        filename = os.path.join(OUTPUT_DIR, f"unknown_{saved}.jpg")
        cv2.imwrite(filename, degraded)
        saved += 1

        if saved % 20 == 0:
            print(f"[PROGRESS] {saved}/{TARGET_COUNT} tersimpan")

        if saved >= TARGET_COUNT:
            break

    print(f"[DONE] Total {saved} foto 'Unknown' tersimpan di {OUTPUT_DIR}")


if __name__ == "__main__":
    prepare_unknown_dataset()