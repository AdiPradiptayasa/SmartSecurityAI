"""Diagnosis satu frame: tahap mana yang gagal dan berapa skornya.

Pakai:  python ai/face/diagnose.py path/frame.jpg
Kalibrasi threshold dari banyak frame ESP32-CAM:
        python ai/face/diagnose.py --calibrate folder_owner folder_unknown
(folder berisi frame nyata dari ESP32-CAM; owner harus sudah ter-enroll)
"""
import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.dirname(__file__))
from classify import FaceClassifier
from preprocess import enhance_if_dark


def diagnose(c, path):
    img = cv2.imread(path)
    if img is None:
        print("[ERROR] gambar tidak terbaca:", path)
        return
    print(f"brightness (gray mean): {cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean():.1f}")

    for name, im in [("asli", img), ("enhanced", enhance_if_dark(img))]:
        yolo = c.detector._raw_predict(im)
        print(f"\n[{name}] YOLO: {[(f['bbox'], round(f['confidence'], 2)) for f in yolo]}")
        full = c.recognizer.app.get(im)
        print(f"[{name}] InsightFace gambar penuh det_score: {[round(float(f.det_score), 2) for f in full]}")
        if full:
            print(f"[{name}] skor owner (gambar penuh): {c._best_match(full[0].embedding)}")
        if yolo:
            crop = c.detector.crop_face(im, yolo[0]['bbox'])
            e = c.recognizer.get_embedding(crop)
            print(f"[{name}] embedding dari crop ketat: {'None' if e is None else c._best_match(e)}")

    print("\n[PIPELINE FINAL]", c.classify_image(img))


def scores_in(c, folder):
    out = []
    for f in sorted(os.listdir(folder)):
        if not f.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        r = c.classify_image(cv2.imread(os.path.join(folder, f)))
        if r["status"] in ("known", "unknown"):
            out.append(r["confidence"] / 100.0)
        else:
            print(f"  {f}: {r['status']}")
    return np.array(out)


def calibrate(c, owner_dir, unknown_dir):
    from sklearn.metrics import roc_curve, roc_auc_score
    pos, neg = scores_in(c, owner_dir), scores_in(c, unknown_dir)
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    s = np.r_[pos, neg]
    fpr, tpr, thr = roc_curve(y, s)
    i = int(np.argmax(tpr - fpr))  # titik Youden
    print(f"owner n={len(pos)} (mean {pos.mean():.3f}) | unknown n={len(neg)} (mean {neg.mean():.3f})")
    print(f"AUC={roc_auc_score(y, s):.4f}")
    print(f"Threshold usulan={thr[i]:.4f}  TPR={tpr[i]:.3f}  FPR={fpr[i]:.3f}")


if __name__ == "__main__":
    clf = FaceClassifier()
    if len(sys.argv) >= 4 and sys.argv[1] == "--calibrate":
        calibrate(clf, sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 2:
        diagnose(clf, sys.argv[1])
    else:
        print(__doc__)
