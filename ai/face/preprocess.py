"""Preprocessing bersama untuk enrollment DAN inference.

Satu fungsi dipakai di semua jalur supaya embedding di database dan embedding
saat inference dihasilkan dari kondisi gambar yang sebanding.
"""
import cv2
import numpy as np

DARK_THRESHOLD = 90  # rata-rata gray di bawah ini dianggap gelap


def is_dark(img, thr=DARK_THRESHOLD):
    return float(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean()) < thr


def enhance_if_dark(img, thr=DARK_THRESHOLD):
    """Gray-world (netralkan color cast hijau) + gamma ringan + CLAHE lembut.
    Gambar yang sudah cukup terang dikembalikan apa adanya."""
    if not is_dark(img, thr):
        return img

    b, g, r = cv2.split(img.astype(np.float32))
    mb, mg, mr = b.mean() + 1e-6, g.mean() + 1e-6, r.mean() + 1e-6
    m = (mb + mg + mr) / 3.0
    balanced = cv2.merge([b * m / mb, g * m / mg, r * m / mr])
    balanced = np.clip(balanced, 0, 255).astype(np.uint8)

    table = ((np.arange(256) / 255.0) ** (1 / 1.6) * 255).astype("uint8")
    balanced = cv2.LUT(balanced, table)

    lab = cv2.cvtColor(balanced, cv2.COLOR_BGR2LAB)
    l, a, bb = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    return cv2.cvtColor(cv2.merge((l, a, bb)), cv2.COLOR_LAB2BGR)
