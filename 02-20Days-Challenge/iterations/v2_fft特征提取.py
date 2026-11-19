import os
import csv
import numpy as np
from scipy.io import wavfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
PLOT_DIR = os.path.join(PROCESSED_DIR, "频谱图")


def extract(wav_path):
    sr, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data[:, 0]
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float64) / np.iinfo(data.dtype).max

    spectrum = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), d=1.0 / sr)
    mag = np.abs(spectrum)
    total = mag.sum()
    if total == 0:
        return None

    peak = float(freqs[np.argmax(mag)])
    low = mag[(freqs >= 0) & (freqs < 500)].sum()
    mid = mag[(freqs >= 500) & (freqs < 2000)].sum()
    high = mag[freqs >= 2000].sum()

    base = os.path.splitext(os.path.basename(wav_path))[0]
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(8, 4))
    plt.plot(freqs, mag)
    plt.title(base)
    plt.xlabel("频率 (Hz)")
    plt.ylabel("幅值")
    plt.xlim(0, 5000)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, base + ".png"))
    plt.close()

    return {
        "file": base,
        "sample_rate": sr,
        "peak_freq": round(peak, 1),
        "low_ratio": round(low / total, 4),
        "mid_ratio": round(mid / total, 4),
        "high_ratio": round(high / total, 4),
    }


def main():
    rows = []
    for f in sorted(os.listdir(PROCESSED_DIR)):
        if f.lower().endswith(".wav"):
            feat = extract(os.path.join(PROCESSED_DIR, f))
            if feat:
                rows.append(feat)

    with open(FEATURE_CSV, "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=["file", "sample_rate", "peak_freq", "low_ratio", "mid_ratio", "high_ratio"])
        w.writeheader()
        w.writerows(rows)

    print("特征已提取:", len(rows), "条 ->", FEATURE_CSV)
    print("频谱图目录:", PLOT_DIR)


if __name__ == "__main__":
    main()