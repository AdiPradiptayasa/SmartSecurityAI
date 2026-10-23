import os
import pickle
import shutil
import uuid
from datetime import datetime

DATASET_DIR = "dataset"
EMBEDDINGS_DB_PATH = "ai/models/owner_embeddings.pkl"

# Folder yang BUKAN owner (data test/unknown)
NON_OWNER_FOLDERS = {"Unknown", "test", "Neighbour", "Mangku", "Ibu"}
READY_THRESHOLD = 30  # minimal foto supaya status "ready"


class AIDataService:
    
    def save_uploaded_photos(self, person_name, files):
        """Simpan foto upload ke dataset/<nama>/, return jumlah yang berhasil"""
        folder_path = os.path.join(DATASET_DIR, person_name)
        os.makedirs(folder_path, exist_ok=True)

        saved_count = 0
        for file in files:
            ext = os.path.splitext(file.filename)[1] or ".jpg"
            unique_name = f"{person_name}_{uuid.uuid4().hex[:8]}{ext}"
            dest_path = os.path.join(folder_path, unique_name)

            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_count += 1

        return saved_count

    def run_enrollment(self):
        """Jalankan ulang proses enrollment (build ulang owner_embeddings.pkl)"""
        import sys
        ai_face_path = os.path.join(os.path.dirname(__file__), "..", "..", "ai", "face")
        if ai_face_path not in sys.path:
            sys.path.append(ai_face_path)

        from enroll import enroll_all_owners
        enroll_all_owners()

        return self.get_owners()

    def _load_enrolled_names(self):
        """Nama-nama yang SUDAH ter-enroll ke database embedding (owner_embeddings.pkl)"""
        if not os.path.exists(EMBEDDINGS_DB_PATH):
            return {}

        with open(EMBEDDINGS_DB_PATH, "rb") as f:
            db = pickle.load(f)

        return {name: len(embeddings) for name, embeddings in db.items()}

    def _folder_image_count(self, folder_path):
        if not os.path.exists(folder_path):
            return 0
        return len([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])

    def _folder_last_modified(self, folder_path):
        if not os.path.exists(folder_path):
            return None

        files = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if not files:
            return None

        latest_file = max(files, key=os.path.getmtime)
        return datetime.fromtimestamp(os.path.getmtime(latest_file))

    def get_owners(self):
        """Daftar owner (bukan Unknown/test) beserta status enrollment-nya"""
        if not os.path.exists(DATASET_DIR):
            return []

        enrolled_names = self._load_enrolled_names()

        owner_folders = [
            f for f in os.listdir(DATASET_DIR)
            if os.path.isdir(os.path.join(DATASET_DIR, f)) and f not in NON_OWNER_FOLDERS
        ]

        owners = []
        for name in owner_folders:
            folder_path = os.path.join(DATASET_DIR, name)
            total_images = self._folder_image_count(folder_path)
            enrolled_count = enrolled_names.get(name, 0)
            last_modified = self._folder_last_modified(folder_path)

            # "registered" kalau sudah ter-enroll ke database AI,
            # "pending" kalau folder ada tapi belum pernah dijalankan enroll.py
            status = "registered" if enrolled_count > 0 else "pending"

            owners.append({
                "name": name,
                "images": total_images,
                "enrolled_embeddings": enrolled_count,
                "status": status,
                "last_seen": last_modified.isoformat() if last_modified else None,
            })

        return owners

    def get_dataset_summary(self):
        """Semua folder di dataset/ (termasuk Unknown & test person), untuk halaman Dataset"""
        if not os.path.exists(DATASET_DIR):
            return []

        all_folders = [
            f for f in os.listdir(DATASET_DIR)
            if os.path.isdir(os.path.join(DATASET_DIR, f))
        ]

        dataset = []
        for name in all_folders:
            folder_path = os.path.join(DATASET_DIR, name)
            total_images = self._folder_image_count(folder_path)
            last_modified = self._folder_last_modified(folder_path)

            status = "ready" if total_images >= READY_THRESHOLD else "incomplete"

            dataset.append({
                "name": name,
                "images": total_images,
                "status": status,
                "updated_at": last_modified.isoformat() if last_modified else None,
            })

        # Urutkan dari yang paling banyak foto
        dataset.sort(key=lambda d: d["images"], reverse=True)
        return dataset