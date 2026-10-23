import insightface
import numpy as np
import cv2

MODEL_NAME = "buffalo_l"


class FaceRecognizer:
    def __init__(self, det_thresh=0.3):
        self.app = insightface.app.FaceAnalysis(
            name=MODEL_NAME,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        # det_thresh diturunkan (default 0.5) agar wajah di gambar gelap/berderau tetap terdeteksi
        self.app.prepare(ctx_id=0, det_thresh=det_thresh, det_size=(640, 640))

    def _try_detect(self, image):
        return self.app.get(image)

    @staticmethod
    def _area(bbox):
        return max(0, bbox[2] - bbox[0]) * max(0, bbox[3] - bbox[1])

    @staticmethod
    def _iou(a, b):
        x1, y1 = max(a[0], b[0]), max(a[1], b[1])
        x2, y2 = min(a[2], b[2]), min(a[3], b[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        union = FaceRecognizer._area(a) + FaceRecognizer._area(b) - inter
        return inter / (union + 1e-9)

    def get_embedding_for_bbox(self, image, bbox, min_iou=0.3):
        """Embedding untuk wajah yang overlap dengan bbox YOLO.
        Memakai GAMBAR PENUH (sama seperti enrollment), bukan crop ketat,
        sehingga alignment SCRFD/ArcFace bekerja dengan konteks yang cukup."""
        faces = self._try_detect(image)
        if not faces:
            return None
        best = max(faces, key=lambda f: self._iou(f.bbox, bbox))
        if self._iou(best.bbox, bbox) < min_iou:
            return None
        return best.embedding

    def get_embedding(self, face_image):
        """Embedding wajah terbesar di gambar (dipakai enrollment & cadangan inference)."""
        h, w = face_image.shape[:2]

        faces = self._try_detect(face_image)

        # Cadangan untuk foto dataset yang di-crop sangat ketat
        if len(faces) == 0 and (w < 200 or h < 200):
            scale = 300 / min(w, h)
            upscaled = cv2.resize(face_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            faces = self._try_detect(upscaled)

        if len(faces) == 0:
            padded = cv2.copyMakeBorder(face_image, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            faces = self._try_detect(padded)

        if len(faces) == 0:
            return None

        largest = max(faces, key=lambda f: self._area(f.bbox))
        return largest.embedding

    def compare(self, embedding1, embedding2):
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        return float(np.dot(embedding1, embedding2))


if __name__ == "__main__":
    import sys

    recognizer = FaceRecognizer()
    test_image_path = sys.argv[1] if len(sys.argv) > 1 else "dataset/Adi Pradipta/Adi Pradipta_1.jpg"
    image = cv2.imread(test_image_path)

    if image is None:
        print(f"[ERROR] Tidak bisa baca gambar: {test_image_path}")
        sys.exit(1)

    embedding = recognizer.get_embedding(image)

    if embedding is None:
        print("[ERROR] Tidak ada wajah terdeteksi InsightFace di gambar ini")
    else:
        print(f"[OK] Embedding berhasil diekstrak, shape: {embedding.shape}")
