import os
import sys
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(__file__))
from detector import FaceDetector
from recognizer import FaceRecognizer

CHALLENGE_SET_DIR = "ai/face/challenge_set"
EMBEDDINGS_DB_PATH = "ai/models/owner_embeddings.pkl"
OUTPUT_DIR = "ai/face/eval_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SIMILARITY_THRESHOLD = 0.6673  # hasil dari evaluasi utama sebelumnya


def load_embeddings_db():
    with open(EMBEDDINGS_DB_PATH, "rb") as f:
        return pickle.load(f)


def get_best_similarity(query_embedding, embeddings_db, recognizer):
    best_similarity = -1.0
    best_name = None
    for name, embeddings_list in embeddings_db.items():
        for known_embedding in embeddings_list:
            sim = recognizer.compare(query_embedding, known_embedding)
            if sim > best_similarity:
                best_similarity = sim
                best_name = name
    return best_name, best_similarity


def scan_challenge_set():
    """Scan struktur folder: challenge_set/<kategori>/<nama_orang>/*.jpg"""
    samples = []

    if not os.path.exists(CHALLENGE_SET_DIR):
        print(f"[ERROR] Folder {CHALLENGE_SET_DIR} tidak ditemukan")
        return samples

    for category in os.listdir(CHALLENGE_SET_DIR):
        category_path = os.path.join(CHALLENGE_SET_DIR, category)
        if not os.path.isdir(category_path):
            continue

        for person_name in os.listdir(category_path):
            person_path = os.path.join(category_path, person_name)
            if not os.path.isdir(person_path):
                continue

            image_files = [f for f in os.listdir(person_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for img_file in image_files:
                samples.append({
                    "category": category,
                    "person_name": person_name,
                    "image_path": os.path.join(person_path, img_file)
                })

    return samples


def run_challenge_evaluation():
    print("[INFO] Memuat model dan database embedding...")
    detector = FaceDetector()
    recognizer = FaceRecognizer()
    embeddings_db = load_embeddings_db()

    samples = scan_challenge_set()
    print(f"[INFO] Ditemukan {len(samples)} foto challenge set")

    if len(samples) == 0:
        print("[ERROR] Tidak ada foto untuk dievaluasi")
        return []

    results = []

    for sample in samples:
        image = cv2.imread(sample["image_path"])
        if image is None:
            continue

        faces = detector.detect(image)

        if len(faces) == 0:
            results.append({
                **sample, "detected": False, "similarity": 0.0,
                "matched_name": None, "correctly_recognized": False
            })
            continue

        best_face = max(faces, key=lambda f: f["confidence"])
        face_crop = detector.crop_face(image, best_face["bbox"])
        if sample["category"] == "Jauh":
            print(f"[DEBUG] Ukuran crop wajah 'Jauh': {face_crop.shape[1]}x{face_crop.shape[0]} px")
        embedding = recognizer.get_embedding(face_crop)

        if embedding is None:
            results.append({
                **sample, "detected": False, "similarity": 0.0,
                "matched_name": None, "correctly_recognized": False
            })
            continue

        matched_name, similarity = get_best_similarity(embedding, embeddings_db, recognizer)

        # "Correctly recognized" = similarity di atas threshold DAN nama yang cocok benar
        is_above_threshold = similarity >= SIMILARITY_THRESHOLD
        is_correct_identity = matched_name == sample["person_name"]
        correctly_recognized = is_above_threshold and is_correct_identity

        results.append({
            **sample, "detected": True, "similarity": similarity,
            "matched_name": matched_name, "correctly_recognized": correctly_recognized
        })

    return results


def analyze_challenge_results(results):
    categories = sorted(set(r["category"] for r in results))

    print(f"\n{'='*60}")
    print(f"HASIL EVALUASI CHALLENGE SET (Kondisi Menantang)")
    print(f"{'='*60}")
    print(f"Threshold yang dipakai: {SIMILARITY_THRESHOLD}")
    print(f"Catatan: Recall di sini mengukur seberapa sering sistem")
    print(f"BENAR mengenali owner meski kondisi sulit (jarak jauh/gelap)")

    breakdown = {}

    for category in categories:
        cat_results = [r for r in results if r["category"] == category]
        n_total = len(cat_results)
        n_detected = sum(1 for r in cat_results if r["detected"])
        n_correct = sum(1 for r in cat_results if r["correctly_recognized"])

        detection_rate = n_detected / n_total if n_total > 0 else 0
        recall = n_correct / n_total if n_total > 0 else 0  # dari total sampel (termasuk yang gagal deteksi)

        detected_sims = [r["similarity"] for r in cat_results if r["detected"]]
        avg_sim = np.mean(detected_sims) if detected_sims else 0.0

        print(f"\n[{category.upper()}]")
        print(f"  Total foto           : {n_total}")
        print(f"  Wajah terdeteksi     : {n_detected} ({detection_rate*100:.1f}%)")
        print(f"  Dikenali benar       : {n_correct} ({recall*100:.1f}%)")
        print(f"  Rata-rata similarity : {avg_sim:.4f}")

        breakdown[category] = {
            "n_total": n_total,
            "detection_rate": detection_rate,
            "recall": recall,
            "avg_similarity": avg_sim
        }

    # ── Visualisasi ──────────────────
    plt.figure(figsize=(8, 5))
    cats = list(breakdown.keys())
    recalls = [breakdown[c]["recall"] for c in cats]
    detection_rates = [breakdown[c]["detection_rate"] for c in cats]

    x = np.arange(len(cats))
    width = 0.35

    plt.bar(x - width/2, detection_rates, width, label='Detection Rate', color='#3b82f6')
    plt.bar(x + width/2, recalls, width, label='Recall (Dikenali Benar)', color='#22c55e')

    plt.xticks(x, cats)
    plt.ylim(0, 1.15)
    plt.ylabel('Rate')
    plt.title('Performa Sistem pada Kondisi Menantang (Challenge Set)')
    plt.legend()

    for i, (dr, rc) in enumerate(zip(detection_rates, recalls)):
        plt.text(i - width/2, dr + 0.02, f'{dr:.1%}', ha='center', fontsize=9)
        plt.text(i + width/2, rc + 0.02, f'{rc:.1%}', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "challenge_set_results.png"), dpi=150)
    plt.close()
    print(f"\n[SAVED] {OUTPUT_DIR}/challenge_set_results.png")

    # ── Simpan ringkasan teks ──────────────────
    summary_path = os.path.join(OUTPUT_DIR, "challenge_summary.txt")
    with open(summary_path, "w") as f:
        f.write("HASIL EVALUASI CHALLENGE SET (Kondisi Menantang)\n")
        f.write("="*60 + "\n\n")
        f.write(f"Threshold: {SIMILARITY_THRESHOLD}\n\n")
        for cat, data in breakdown.items():
            f.write(f"[{cat.upper()}]\n")
            f.write(f"  Total foto: {data['n_total']}\n")
            f.write(f"  Detection rate: {data['detection_rate']:.4f}\n")
            f.write(f"  Recall: {data['recall']:.4f}\n")
            f.write(f"  Avg similarity: {data['avg_similarity']:.4f}\n\n")

    print(f"[SAVED] {summary_path}")

    return breakdown


if __name__ == "__main__":
    results = run_challenge_evaluation()
    if results:
        analyze_challenge_results(results)