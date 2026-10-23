from ultralytics import YOLO
import cv2
import numpy as np

from preprocess import enhance_if_dark

MODEL_PATH = "ai/models/yolov8n-face-lindevs.pt"


class FaceDetector:
    def __init__(self, confidence_threshold=0.30):
        self.model = YOLO(MODEL_PATH)
        self.confidence_threshold = confidence_threshold

    def _raw_predict(self, image, imgsz=640):
        results = self.model.predict(image, conf=self.confidence_threshold, imgsz=imgsz, verbose=False)
        faces = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0].cpu().numpy())
                faces.append({"bbox": (int(x1), int(y1), int(x2), int(y2)), "confidence": confidence})
        return faces

    def detect(self, image, auto_enhance=False):
        """auto_enhance default False: enhancement dilakukan SEKALI di classifier
        dan gambar yang sama dipakai untuk YOLO maupun ArcFace."""
        processed_image = enhance_if_dark(image) if auto_enhance else image

        # Strategi 1: langsung
        faces = self._raw_predict(processed_image)

        # Strategi 2: input YOLO lebih besar (membantu wajah kecil), tanpa mengubah piksel gambar
        if len(faces) == 0:
            faces = self._raw_predict(processed_image, imgsz=1024)

        # Strategi 3: padding (wajah menempel tepi frame)
        if len(faces) == 0:
            pad = 60
            padded = cv2.copyMakeBorder(processed_image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            faces = self._raw_predict(padded)
            for face in faces:
                x1, y1, x2, y2 = face["bbox"]
                face["bbox"] = (max(0, x1 - pad), max(0, y1 - pad), max(0, x2 - pad), max(0, y2 - pad))

        return faces

    def crop_face(self, image, bbox, margin=0.2):
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        box_w, box_h = x2 - x1, y2 - y1
        x1 = max(0, int(x1 - box_w * margin))
        y1 = max(0, int(y1 - box_h * margin))
        x2 = min(w, int(x2 + box_w * margin))
        y2 = min(h, int(y2 + box_h * margin))
        return image[y1:y2, x1:x2]


if __name__ == "__main__":
    import sys

    detector = FaceDetector()
    test_image_path = sys.argv[1] if len(sys.argv) > 1 else "dataset/Adi Pradipta/Adi Pradipta_1.jpg"
    image = cv2.imread(test_image_path)

    if image is None:
        print(f"[ERROR] Tidak bisa baca gambar: {test_image_path}")
        sys.exit(1)

    faces = detector.detect(enhance_if_dark(image))
    print(f"[INFO] Ditemukan {len(faces)} wajah")

    for i, face in enumerate(faces):
        print(f"  Wajah {i+1}: bbox={face['bbox']}, confidence={face['confidence']:.2f}")
        x1, y1, x2, y2 = face['bbox']
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imwrite("ai/face/test_output.jpg", image)
    print("[OK] Hasil visualisasi disimpan di ai/face/test_output.jpg")
