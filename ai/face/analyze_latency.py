import csv
import numpy as np
import matplotlib.pyplot as plt
import os


LATENCY_LOG_PATH = "server/logs/latency_log.csv"
OUTPUT_DIR = "ai/face/eval_results"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_latency_data():

    rows = []

    with open(
        LATENCY_LOG_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)

    return rows


def analyze():

    rows = load_latency_data()

    if len(rows) == 0:

        print(
            "[ERROR] Belum ada data latency. "
            "Jalankan sistem dan trigger motion beberapa kali dulu."
        )

        return

    print(
        f"[INFO] Total {len(rows)} pengukuran ditemukan\n"
    )


    # =========================================================
    # DEFINISI TAHAP PENGUJIAN
    # =========================================================

    stages = {

        "Motion → Capture (ESP32-CAM)":
            "t_motion_to_capture_ms",

        "Capture → AI Classification":
            "t_capture_to_ai_ms",

        "AI → Simpan Database":
            "t_ai_to_dbsave_ms",

        "Database → Kirim Telegram":
            "t_dbsave_to_telegram_ms",

        "TOTAL (Motion → Telegram)":
            "t_total_ms",
    }


    # =========================================================
    # PERHITUNGAN STATISTIK
    # =========================================================

    summary = {}


    print(
        f"{'Tahap':<35}"
        f"{'Rata-rata':>10}"
        f"{'Std Dev':>10}"
        f"{'Min':>8}"
        f"{'Max':>8}  (ms)"
    )

    print("=" * 80)


    for label, key in stages.items():

        values = np.array(
            [
                float(r[key])
                for r in rows
                if r.get(key) not in ("", None)
            ]
        )

        if len(values) == 0:

            print(
                f"{label:<35} DATA TIDAK TERSEDIA"
            )

            continue


        mean = np.mean(values)
        std = np.std(values)
        vmin = np.min(values)
        vmax = np.max(values)


        summary[label] = {

            "mean": mean,
            "std": std,
            "min": vmin,
            "max": vmax

        }


        print(
            f"{label:<35}"
            f"{mean:>10.1f}"
            f"{std:>10.1f}"
            f"{vmin:>8.1f}"
            f"{vmax:>8.1f}"
        )


    # =========================================================
    # VISUALISASI 1
    # RATA-RATA WAKTU SETIAP TAHAP
    # =========================================================

    stage_labels = list(stages.keys())[:-1]

    stage_means = [
        summary[label]["mean"]
        for label in stage_labels
        if label in summary
    ]


    plt.figure(figsize=(9, 5))


    colors = [
        "#3b82f6",
        "#8b5cf6",
        "#22c55e",
        "#f59e0b"
    ]


    bars = plt.bar(
        range(len(stage_means)),
        stage_means,
        color=colors[:len(stage_means)]
    )


    for bar, val in zip(
        bars,
        stage_means
    ):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            val + 5,
            f"{val:.0f} ms",
            ha="center",
            fontsize=9
        )


    plt.xticks(
        range(len(stage_means)),
        [
            label.replace(
                " → ",
                "\n→ "
            )
            for label in stage_labels
        ],
        fontsize=8
    )


    plt.ylabel(
        "Waktu rata-rata (ms)"
    )


    plt.title(
        f"Rata-rata Waktu Tiap Tahap Pemrosesan "
        f"(n={len(rows)} pengujian)"
    )


    plt.tight_layout()


    breakdown_path = os.path.join(
        OUTPUT_DIR,
        "latency_breakdown.png"
    )


    plt.savefig(
        breakdown_path,
        dpi=150
    )

    plt.close()


    print(
        f"\n[SAVED] {breakdown_path}"
    )


    # =========================================================
    # VISUALISASI 2
    # BOXPLOT TOTAL LATENCY
    # =========================================================

    total_values = np.array(
        [
            float(r["t_total_ms"])
            for r in rows
            if r.get("t_total_ms") not in ("", None)
        ]
    )


    plt.figure(figsize=(6, 5))


    plt.boxplot(
        total_values,
        vert=True,
        patch_artist=True,
        boxprops=dict(
            facecolor="#3b82f6",
            alpha=0.6
        )
    )


    plt.ylabel(
        "Waktu Total (ms)"
    )


    plt.title(
        f"Distribusi Waktu Tanggap End-to-End "
        f"(n={len(total_values)})"
    )


    plt.xticks(
        [1],
        ["Motion → Notifikasi Telegram"]
    )


    plt.tight_layout()


    boxplot_path = os.path.join(
        OUTPUT_DIR,
        "latency_boxplot.png"
    )


    plt.savefig(
        boxplot_path,
        dpi=150
    )

    plt.close()


    print(
        f"[SAVED] {boxplot_path}"
    )


    # =========================================================
    # SIMPAN HASIL ANALISIS
    # =========================================================

    summary_path = os.path.join(
        OUTPUT_DIR,
        "latency_summary.txt"
    )


    # PENTING:
    # encoding="utf-8" memperbaiki UnicodeEncodeError
    # pada karakter "→"

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "HASIL PENGUKURAN WAKTU TANGGAP SISTEM\n"
        )

        f.write(
            "=" * 60 + "\n\n"
        )

        f.write(
            f"Jumlah pengujian: {len(rows)}\n\n"
        )


        for label, data in summary.items():

            f.write(
                f"{label}:\n"
            )

            f.write(
                f"  Rata-rata : "
                f"{data['mean']:.1f} ms\n"
            )

            f.write(
                f"  Std Dev   : "
                f"{data['std']:.1f} ms\n"
            )

            f.write(
                f"  Min       : "
                f"{data['min']:.1f} ms\n"
            )

            f.write(
                f"  Max       : "
                f"{data['max']:.1f} ms\n\n"
            )


    print(
        f"[SAVED] {summary_path}"
    )


    return summary


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    analyze()