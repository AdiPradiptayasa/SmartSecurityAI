import cv2
import os
import time
import requests
import numpy as np

ESP32CAM_STREAM_URL = "http://192.168.137.50:81/stream"
OUTPUT_DIR = "ai/face/challenge_set"


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


def capture_challenge_photos(category, person_name, num_images=15):
    """
    category: nama kondisi, misal 'jauh', 'gelap', 'jauh_gelap'
    person_name: nama orang yang difoto (harus SAMA dengan nama di dataset utama, misal 'Adi Pradipta' atau 'Mangku')
    """
    save_dir = os.path.join(OUTPUT_DIR, category, person_name)
    os.makedirs(save_dir, exist_ok=True)

    print(f"[INFO] Capture kondisi '{category}' untuk '{person_name}'")
    print(f"[INFO] TIDAK ada filter kualitas — semua frame yang kamu ambil akan tersimpan")
    print(f"[INFO] Tekan SPASI untuk capture manual, 'q' untuk selesai")

    count = 0
    for frame in get_mjpeg_frame_generator(ESP32CAM_STREAM_URL):
        display = frame.copy()
        cv2.putText(display, f"[{category}] {person_name}: {count}/{num_images} - SPASI=capture, Q=keluar",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Challenge Set Capture", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            filename = os.path.join(save_dir, f"{person_name}_{category}_{count}.jpg")
            cv2.imwrite(filename, frame)  # simpan FRAME UTUH, bukan crop
            count += 1
            print(f"[CAPTURE] {count}/{num_images}")
        elif key == ord('q') or count >= num_images:
            break

    cv2.destroyAllWindows()
    print(f"[DONE] {count} foto tersimpan di {save_dir}")


if __name__ == "__main__":
    print("Kondisi yang tersedia: jauh, gelap, jauh_gelap, miring (sudut ekstrem)")
    category = input("Kategori kondisi: ")
    person_name = input("Nama orang (harus SAMA dengan nama di dataset/): ")
    jumlah = int(input("Jumlah foto (rekomendasi 10-15): "))
    capture_challenge_photos(category, person_name, jumlah)