import os
import sys
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score,
    recall_score, f1_score, roc_curve, auc
)

sys.path.append(os.path.dirname(__file__))
from detector import FaceDetector
from recognizer import FaceRecognizer

TEST_SPLIT_PATH = "ai/models/test_split.pkl"
EMBEDDINGS_DB_PATH = "ai/models/owner_embeddings.pkl"
UNKNOWN_DIR = "dataset/Unknown"
REAL_UNKNOWN_FOLDERS = ["Mangku", "Ibu"]

OUTPUT_DIR = "ai/face/eval_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Threshold kategorisasi (proxy, karena tidak ada data jarak/lux sesungguhnya)
BRIGHTNESS_DARK_MAX = 90
BRIGHTNESS_BRIGHT_MIN = 180

DISTANCE_CLOSE_MIN_RATIO = 0.15   # wajah > 15% dari frame = dekat
DISTANCE_FAR_MAX_RATIO = 0.05     # wajah < 5% dari frame = jauh


def categorize_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)

    if mean_brightness < BRIGHTNESS_DARK_MAX:
        return "Gelap"
    elif mean_brightness > BRIGHTNESS_BRIGHT_MIN:
        return "Terang"
    else:
        return "Normal"


def categorize_distance(bbox, image_shape):
    x1, y1, x2, y2 = bbox
    face_area = (x2 - x1) * (y2 - y1)
    frame_area = image_shape[0] * image_shape[1]
    ratio = face_area / frame_area

    if ratio >= DISTANCE_CLOSE_MIN_RATIO:
        return "Dekat"
    elif ratio <= DISTANCE_FAR_MAX_RATIO:
        return "Jauh"
    else:
        return "Sedang"


def load_data():
    with open(TEST_SPLIT_PATH, "rb") as f:
        test_split = pickle.load(f)
    with open(EMBEDDINGS_DB_PATH, "rb") as f:
        embeddings_db = pickle.load(f)
    return test_split, embeddings_db


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


def process_single_image(img_path, true_label, true_name, source, detector, recognizer, embeddings_db):
    """Proses 1 gambar lengkap: deteksi, recognition, DAN kategorisasi kondisi"""
    image = cv2.imread(img_path)
    if image is None:
        return None

    base_result = {
        "true_label": true_label, "true_name": true_name,
        "image_path": img_path, "source": source,
        "brightness_category": categorize_brightness(image),
    }

    faces = detector.detect(image)
    if len(faces) == 0:
        base_result.update({
            "similarity": 0.0, "matched_name": None,
            "detected": False, "distance_category": "N/A"
        })
        return base_result

    best_face = max(faces, key=lambda f: f["confidence"])
    distance_cat = categorize_distance(best_face["bbox"], image.shape)

    face_crop = detector.crop_face(image, best_face["bbox"])
    embedding = recognizer.get_embedding(face_crop)

    if embedding is None:
        base_result.update({
            "similarity": 0.0, "matched_name": None,
            "detected": False, "distance_category": distance_cat
        })
        return base_result

    matched_name, similarity = get_best_similarity(embedding, embeddings_db, recognizer)
    base_result.update({
        "similarity": similarity, "matched_name": matched_name,
        "detected": True, "distance_category": distance_cat
    })
    return base_result


def run_evaluation():
    print("[INFO] Memuat model dan data...")
    detector = FaceDetector()
    recognizer = FaceRecognizer()
    test_split, embeddings_db = load_data()

    results = []

    print("\n[EVALUASI] Testing foto owner (held-out test set)...")
    for owner_name, image_paths in test_split.items():
        for img_path in image_paths:
            r = process_single_image(img_path, "known", owner_name, "owner", detector, recognizer, embeddings_db)
            if r:
                results.append(r)
        print(f"  {owner_name}: {len(image_paths)} foto diproses")

    print("\n[EVALUASI] Testing foto Unknown (sumber: LFW)...")
    unknown_files = [f for f in os.listdir(UNKNOWN_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    for img_file in unknown_files:
        img_path = os.path.join(UNKNOWN_DIR, img_file)
        r = process_single_image(img_path, "unknown", "Unknown-LFW", "lfw", detector, recognizer, embeddings_db)
        if r:
            results.append(r)
    print(f"  Unknown (LFW): {len(unknown_files)} foto diproses")

    print("\n[EVALUASI] Testing foto Unknown (sumber: ESP32-CAM asli)...")
    for real_unknown_name in REAL_UNKNOWN_FOLDERS:
        folder_path = os.path.join("dataset", real_unknown_name)
        if not os.path.exists(folder_path):
            print(f"  [SKIP] Folder {folder_path} tidak ditemukan")
            continue
        real_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for img_file in real_files:
            img_path = os.path.join(folder_path, img_file)
            r = process_single_image(img_path, "unknown", f"Unknown-Real-{real_unknown_name}", "real_camera", detector, recognizer, embeddings_db)
            if r:
                results.append(r)
        print(f"  {real_unknown_name}: {len(real_files)} foto diproses")

    return results


def analyze_by_condition(results, condition_key, condition_label, threshold):
    """Hitung accuracy per kategori kondisi (misal per 'Dekat'/'Sedang'/'Jauh')"""
    detected = [r for r in results if r["detected"]]
    categories = sorted(set(r[condition_key] for r in detected if r[condition_key] != "N/A"))

    print(f"\n{'='*60}")
    print(f"BREAKDOWN PER {condition_label.upper()}")
    print(f"{'='*60}")

    breakdown = {}
    for cat in categories:
        cat_results = [r for r in detected if r[condition_key] == cat]
        y_true = [1 if r["true_label"] == "known" else 0 for r in cat_results]
        y_pred = [1 if r["similarity"] >= threshold else 0 for r in cat_results]

        if len(set(y_true)) < 2:
            # Cuma ada 1 kelas di kategori ini, accuracy tetap bisa dihitung tapi precision/recall bisa tidak valid
            acc = accuracy_score(y_true, y_pred) if len(y_true) > 0 else 0
            print(f"  {cat}: n={len(cat_results)}, accuracy={acc:.3f} (catatan: hanya 1 kelas di kategori ini)")
            breakdown[cat] = {"n": len(cat_results), "accuracy": acc}
            continue

        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)

        print(f"  {cat}: n={len(cat_results)}, accuracy={acc:.3f}, precision={prec:.3f}, recall={rec:.3f}")
        breakdown[cat] = {"n": len(cat_results), "accuracy": acc, "precision": prec, "recall": rec}

    # Visualisasi bar chart
    if breakdown:
        cats = list(breakdown.keys())
        accs = [breakdown[c]["accuracy"] for c in cats]

        plt.figure(figsize=(7, 5))
        bars = plt.bar(cats, accs, color=['#22c55e' if a >= 0.9 else '#f97316' if a >= 0.7 else '#ef4444' for a in accs])
        for bar, acc in zip(bars, accs):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{acc:.2%}', ha='center')
        plt.ylim(0, 1.15)
        plt.ylabel('Accuracy')
        plt.title(f'Accuracy per Kondisi {condition_label}')
        plt.tight_layout()
        filename = f"accuracy_by_{condition_key}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150)
        plt.close()
        print(f"[SAVED] {OUTPUT_DIR}/{filename}")

    return breakdown


def analyze_results(results):
    detected_results = [r for r in results if r["detected"]]
    not_detected = [r for r in results if not r["detected"]]

    print(f"\n{'='*60}")
    print(f"RINGKASAN DETEKSI WAJAH")
    print(f"{'='*60}")
    print(f"Total sampel      : {len(results)}")
    print(f"Wajah terdeteksi  : {len(detected_results)} ({len(detected_results)/len(results)*100:.1f}%)")
    print(f"Gagal terdeteksi  : {len(not_detected)} ({len(not_detected)/len(results)*100:.1f}%)")

    lfw_results = [r for r in detected_results if r.get("source") == "lfw"]
    real_results = [r for r in detected_results if r.get("source") == "real_camera"]

    if real_results:
        print(f"\n{'='*60}")
        print(f"PERBANDINGAN: Unknown dari LFW vs Unknown dari ESP32-CAM Asli")
        print(f"{'='*60}")
        lfw_sims = [r["similarity"] for r in lfw_results]
        real_sims = [r["similarity"] for r in real_results]
        print(f"LFW    - rata-rata similarity: {np.mean(lfw_sims):.4f} (n={len(lfw_sims)})")
        print(f"Kamera - rata-rata similarity: {np.mean(real_sims):.4f} (n={len(real_sims)})")

    y_true = [1 if r["true_label"] == "known" else 0 for r in detected_results]
    similarities = [r["similarity"] for r in detected_results]

    fpr, tpr, thresholds = roc_curve(y_true, similarities)
    roc_auc = auc(fpr, tpr)
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]

    print(f"\n{'='*60}")
    print(f"ANALISIS ROC CURVE")
    print(f"{'='*60}")
    print(f"AUC (Area Under Curve) : {roc_auc:.4f}")
    print(f"Threshold optimal      : {optimal_threshold:.4f}")

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='#2563eb', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random guess')
    plt.scatter(fpr[optimal_idx], tpr[optimal_idx], color='red', zorder=5, label=f'Threshold optimal = {optimal_threshold:.3f}')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Face Recognition (Owner vs Unknown)')
    plt.legend(loc='lower right')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "roc_curve.png"), dpi=150)
    plt.close()
    print(f"[SAVED] {OUTPUT_DIR}/roc_curve.png")

    known_sims = [r["similarity"] for r in detected_results if r["true_label"] == "known"]
    plt.figure(figsize=(9, 5))
    plt.hist(known_sims, bins=30, alpha=0.6, label='Owner (known)', color='#22c55e')
    if lfw_results:
        plt.hist([r["similarity"] for r in lfw_results], bins=30, alpha=0.5, label='Unknown (LFW)', color='#f97316')
    if real_results:
        plt.hist([r["similarity"] for r in real_results], bins=30, alpha=0.6, label='Unknown (ESP32-CAM asli)', color='#ef4444')
    plt.axvline(optimal_threshold, color='black', linestyle='--', label=f'Threshold optimal ({optimal_threshold:.3f})')
    plt.xlabel('Similarity Score')
    plt.ylabel('Jumlah Sampel')
    plt.title('Distribusi Similarity Score: Owner vs Unknown (per sumber)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "similarity_distribution.png"), dpi=150)
    plt.close()
    print(f"[SAVED] {OUTPUT_DIR}/similarity_distribution.png")

    y_pred = [1 if sim >= optimal_threshold else 0 for sim in similarities]
    cm = confusion_matrix(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"\n{'='*60}")
    print(f"METRIK EVALUASI KESELURUHAN (threshold = {optimal_threshold:.4f})")
    print(f"{'='*60}")
    print(f"Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1:.4f}")

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Unknown', 'Owner'], yticklabels=['Unknown', 'Owner'])
    plt.xlabel('Prediksi')
    plt.ylabel('Ground Truth')
    plt.title(f'Confusion Matrix (threshold={optimal_threshold:.3f})')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"), dpi=150)
    plt.close()
    print(f"[SAVED] {OUTPUT_DIR}/confusion_matrix.png")

    # ── Breakdown per kondisi (INI BAGIAN BARU) ──────────────────
    brightness_breakdown = analyze_by_condition(results, "brightness_category", "Pencahayaan", optimal_threshold)
    distance_breakdown = analyze_by_condition(results, "distance_category", "Jarak (estimasi)", optimal_threshold)

    # ── Simpan ringkasan teks ──────────────────
    summary_path = os.path.join(OUTPUT_DIR, "summary.txt")
    with open(summary_path, "w") as f:
        f.write("HASIL EVALUASI SISTEM FACE RECOGNITION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total sampel: {len(results)}\n")
        f.write(f"Wajah terdeteksi: {len(detected_results)} ({len(detected_results)/len(results)*100:.1f}%)\n")
        f.write(f"Gagal terdeteksi: {len(not_detected)} ({len(not_detected)/len(results)*100:.1f}%)\n\n")
        f.write(f"AUC: {roc_auc:.4f}\n")
        f.write(f"Threshold optimal: {optimal_threshold:.4f}\n\n")
        f.write(f"Accuracy Keseluruhan: {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1-Score: {f1:.4f}\n\n")
        f.write(f"Confusion Matrix:\n{cm}\n\n")

        f.write("Breakdown per Pencahayaan:\n")
        for cat, data in brightness_breakdown.items():
            f.write(f"  {cat}: n={data['n']}, accuracy={data['accuracy']:.4f}\n")

        f.write("\nBreakdown per Jarak (estimasi):\n")
        for cat, data in distance_breakdown.items():
            f.write(f"  {cat}: n={data['n']}, accuracy={data['accuracy']:.4f}\n")

    print(f"\n[SAVED] {summary_path}")

    return optimal_threshold


if __name__ == "__main__":
    results = run_evaluation()
    optimal_threshold = analyze_results(results)

    print(f"\n{'='*60}")
    print(f"REKOMENDASI: Update SIMILARITY_THRESHOLD di classify.py")
    print(f"menjadi {optimal_threshold:.4f}")
    print(f"{'='*60}")