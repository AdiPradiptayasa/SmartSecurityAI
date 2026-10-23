from pathlib import Path
from datetime import datetime

DATASET_PATH = Path("dataset")


class DatasetService:

    def get_persons(self):
        persons = []

        if DATASET_PATH.exists():
            for folder in DATASET_PATH.iterdir():
                if folder.is_dir():
                    persons.append(folder.name)

        return sorted(persons)

    def count_images(self, person: str):

        folder = DATASET_PATH / person

        if not folder.exists():
            return 0

        images = list(folder.glob("*.jpg"))

        return len(images)

    def generate_filename(self, person: str):

        total = self.count_images(person)

        filename = f"{person}_{total+1:06d}.jpg"

        return filename

    def create_folder(self, person: str):

        folder = DATASET_PATH / person

        folder.mkdir(parents=True, exist_ok=True)

        return folder

    # ================================
    # Fungsi baru
    # ================================
    def save_image(self, person: str, image_bytes: bytes):

        # Pastikan folder ada
        folder = self.create_folder(person)

        # Nama file otomatis
        filename = self.generate_filename(person)

        filepath = folder / filename

        # Simpan file JPG
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        return {
            "status": "success",
            "person": person,
            "filename": filename,
            "filepath": str(filepath),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }