import sys
import os
import pickle
import numpy as np
import cv2

sys.path.append(os.path.dirname(__file__))
from detector import FaceDetector
from recognizer import FaceRecognizer
from preprocess import enhance_if_dark

EMBEDDINGS_DB_PATH = "ai/models/owner_embeddings.pkl"
# Kalibrasi ulang dari frame ESP32-CAM (lihat diagnose.py); 0.65 hanya nilai awal.
SIMILARITY_THRESHOLD = 0.50


class FaceClassifier:
    def __init__(self, threshold=SIMILARITY_THRESHOLD):
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.threshold = threshold
        self._build_matrix(self._load_embeddings_db())

    def _load_embeddings_db(self):
        if not os.path.exists(EMBEDDINGS_DB_PATH):
            raise FileNotFoundError(
                f"Database embedding tidak ditemukan di {EMBEDDINGS_DB_PATH}. "
                "Jalankan ai/face/enroll.py terlebih dahulu."
            )
        with open(EMBEDDINGS_DB_PATH, "rb") as f:
            return pickle.load(f)

    def _build_matrix(self, db):
        """Satu matriks (N, 512) ternormalisasi -> pencocokan dengan 1 perkalian matriks."""
        self.names = [n for n, lst in db.items() for _ in lst]
        mat = np.vstack([e for lst in db.values() for e in lst]).astype(np.float32)
        self.matrix = mat / np.linalg.norm(mat, axis=1, keepdims=True)

    def _best_match(self, query_embedding):
        q = query_embedding.astype(np.float32)
        q = q / np.linalg.norm(q)
        sims = self.matrix @ q
        i = int(np.argmax(sims))
        return self.names[i], float(sims[i])

    @staticmethod
    def _face_score(f):
        x1, y1, x2, y2 = f["bbox"]
        return f["confidence"] * max(1, (x2 - x1) * (y2 - y1))

    def classify_image(self, image):
        """
        Return dict:
            status    : "known" | "unknown" | "no_face" | "embedding_failed"
            person    : nama / "Unknown" / None
            confidence: similarity * 100
            bbox      : bbox wajah (jika ada)
        """
        # Enhance SEKALI; gambar yang sama dipakai untuk YOLO dan ArcFace
        enhanced = enhance_if_dark(image)

        faces = self.detector.detect(enhanced, auto_enhance=False)
        if len(faces) == 0:
            return {"status": "no_face", "person": None, "confidence": 0.0, "bbox": None}

        best_face = max(faces, key=self._face_score)
        bbox = best_face["bbox"]

        # Utama: gambar penuh + pencocokan bbox (jalur sama dengan enrollment)
        embedding = self.recognizer.get_embedding_for_bbox(enhanced, bbox)
        # Cadangan: wajah terbesar di gambar penuh
        if embedding is None:
            embedding = self.recognizer.get_embedding(enhanced)
        if embedding is None:
            return {"status": "embedding_failed", "person": None, "confidence": 0.0, "bbox": bbox}

        matched_name, similarity = self._best_match(embedding)
        known = similarity >= self.threshold
        return {
            "status": "known" if known else "unknown",
            "person": matched_name if known else "Unknown",
            "confidence": round(similarity * 100, 2),
            "bbox": bbox,
        }

    def classify_burst(self, images):
        """Untuk burst 3-5 frame dari ESP32-CAM: ambil hasil terbaik.
        Known dengan similarity tertinggi menang; jika tidak ada, unknown tertinggi;
        no_face/embedding_failed hanya jika semua frame gagal."""
        results = [self.classify_image(im) for im in images]
        known = [r for r in results if r["status"] == "known"]
        if known:
            return max(known, key=lambda r: r["confidence"])
        unknown = [r for r in results if r["status"] == "unknown"]
        if unknown:
            return max(unknown, key=lambda r: r["confidence"])
        failed = [r for r in results if r["status"] == "embedding_failed"]
        return failed[0] if failed else results[0]


if __name__ == "__main__":
    classifier = FaceClassifier()

    test_image_path = sys.argv[1] if len(sys.argv) > 1 else "server/uploads/events/20260730_025957.jpg"
    image = cv2.imread(test_image_path)

    if image is None:
        print(f"[ERROR] Tidak bisa baca gambar: {test_image_path}")
        sys.exit(1)

    result = classifier.classify_image(image)

    print(f"\n[HASIL KLASIFIKASI]")
    print(f"  Status     : {result['status']}")
    print(f"  Person     : {result['person']}")
    print(f"  Confidence : {result['confidence']}%")
    print(f"  BBox       : {result['bbox']}")

    if result["bbox"]:
        x1, y1, x2, y2 = result["bbox"]
        color = (0, 255, 0) if result["status"] == "known" else (0, 0, 255)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = f"{result['person']} ({result['confidence']}%)"
        cv2.putText(image, label, (x1, max(15, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imwrite("ai/face/classify_output.jpg", image)
    print("\n[OK] Hasil visualisasi disimpan di ai/face/classify_output.jpg")
