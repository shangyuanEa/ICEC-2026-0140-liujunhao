import os
import csv
import numpy as np
from scipy.io import wavfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 基于脚本所在目录算绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
PLOT_DIR = os.path.join(PROCESSED_DIR, "频谱图")

def extract_feature(wav_path):
    sample_rate, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data[:, 0]
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float64) / np.iinfo(data.dtype).max
    n = len(data)
    spectrum = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitude = np.abs(spectrum)
    total_energy = np.sum(magnitude)
    if total_energy == 0:
        return None
    peak_freq = freqs[np.argmax(magnitude)]
    low = magnitude[(freqs >= 0) & (freqs < 500)]
    mid = magnitude[(freqs >= 500) & (freqs < 2000)]
    high = magnitude[(freqs >= 2000)]
    low_ratio = np.sum(low) / total_energy
    mid_ratio = np.sum(mid) / total_energy
    high_ratio = np.sum(high) / total_energy
    os.makedirs(PLOT_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(wav_path))[0]
    plt.figure(figsize=(8, 4))
    plt.plot(freqs, magnitude)
    plt.title(base)
    plt.xlabel("频率 (Hz)")
    plt.ylabel("幅值")
    plt.xlim(0, 5000)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, base + ".png"))
    plt.close()
    return {
        "file": base,
        "peak_freq": round(float(peak_freq), 1),
        "low_ratio": round(float(low_ratio), 4),
        "mid_ratio": round(float(mid_ratio), 4),
        "high_ratio": round(float(high_ratio), 4),
    }

def main():
    rows = []
    for f in sorted(os.listdir(PROCESSED_DIR)):
        if f.lower().endswith(".wav"):
            feat = extract_feature(os.path.join(PROCESSED_DIR, f))
            if feat:
                rows.append(feat)
    with open(FEATURE_CSV, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=["file", "peak_freq", "low_ratio", "mid_ratio", "high_ratio"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"特征已提取：{len(rows)} 条，保存至 {FEATURE_CSV}")
    print("频谱图已保存至", PLOT_DIR)

if __name__ == "__main__":
    main()