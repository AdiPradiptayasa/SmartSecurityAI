import os
import pickle
import random
import cv2
from recognizer import FaceRecognizer
from preprocess import enhance_if_dark

DATASET_DIR = "dataset"
OUTPUT_PATH = "ai/models/owner_embeddings.pkl"
TEST_SPLIT_PATH = "ai/models/test_split.pkl"

EXCLUDED_FOLDERS = {"Unknown", "Neighbour", "Ibu", "Mangku"}
TEST_RATIO = 0.2

# Opsional: frame ESP32-CAM tambahan untuk enrollment, di folder TERPISAH dari dataset/.
# Struktur: esp32_enroll/<NamaOwner>/*.jpg  (folder tidak ada = dilewati)
EXTRA_ENROLL_DIR = "esp32_enroll"

random.seed(42)


def enroll_all_owners():
    recognizer = FaceRecognizer()
    embeddings_db = {}
    test_split = {}

    owner_folders = [
        f for f in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, f)) and f not in EXCLUDED_FOLDERS
    ]

    print(f"[INFO] Ditemukan {len(owner_folders)} owner: {owner_folders}")

    for owner_name in owner_folders:
        folder_path = os.path.join(DATASET_DIR, owner_name)
        # Tanpa sorted(): urutan & hasil shuffle sama persis dengan versi lama,
        # jadi pembagian train/test dataset lama TIDAK berubah.
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        random.shuffle(image_files)
        split_idx = int(len(image_files) * (1 - TEST_RATIO))
        train_files = image_files[:split_idx]
        test_files = image_files[split_idx:]

        print(f"\n[PROCESS] Owner: {owner_name}")
        print(f"  Train: {len(train_files)} foto | Test (disisihkan): {len(test_files)} foto")

        embeddings = []
        failed_count = 0

        train_paths = [os.path.join(folder_path, f) for f in train_files]
        extra_dir = os.path.join(EXTRA_ENROLL_DIR, owner_name)
        if os.path.isdir(extra_dir):
            extra = [os.path.join(extra_dir, f) for f in sorted(os.listdir(extra_dir))
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"  Tambahan frame ESP32-CAM: {len(extra)} foto")
            train_paths += extra

        for img_path in train_paths:
            image = cv2.imread(img_path)
            if image is None:
                failed_count += 1
                continue

            # Preprocessing SAMA dengan jalur inference
            image = enhance_if_dark(image)

            embedding = recognizer.get_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                failed_count += 1

        print(f"  [ENROLLMENT] {len(embeddings)} berhasil, {failed_count} gagal")

        if len(embeddings) > 0:
            embeddings_db[owner_name] = embeddings

        test_split[owner_name] = [os.path.join(folder_path, f) for f in test_files]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(embeddings_db, f)

    with open(TEST_SPLIT_PATH, "wb") as f:
        pickle.dump(test_split, f)

    print(f"\n[DONE] Database embedding tersimpan di {OUTPUT_PATH}")
    print(f"[DONE] Daftar test split tersimpan di {TEST_SPLIT_PATH}")
    for name, embs in embeddings_db.items():
        print(f"  - {name}: {len(embs)} embedding (enrollment)")
        print(f"  - {name}: {len(test_split[name])} foto (test, TIDAK ikut enrollment)")


if __name__ == "__main__":
    enroll_all_owners()
