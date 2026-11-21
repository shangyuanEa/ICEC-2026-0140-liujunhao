import os
import csv
import sys
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

def load_done_files():
    """读已有特征表，返回已处理过的文件名集合"""
    done = set()
    if os.path.isfile(FEATURE_CSV):
        with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
            for row in csv.DictReader(fp):
                done.add(row["file"])
    return done

def extract_feature(wav_path):
    sample_rate, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data[:, 0]
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float64) / np.iinfo(data.dtype).max
    data = data - np.mean(data)
    window = np.hanning(len(data))
    n = len(data)
    spectrum = np.fft.rfft(data * window)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitude = np.abs(spectrum)
    total_energy = np.sum(magnitude)
    if total_energy == 0:
        return None
    peak_freq = freqs[np.argmax(magnitude)]
    low = magnitude[(freqs >= 0) & (freqs < 500)]
    mid = magnitude[(freqs >= 500) & (freqs < 2000)]
    high = magnitude[(freqs >= 2000)]
    return {
        "file": os.path.splitext(os.path.basename(wav_path))[0],
        "sample_rate": sample_rate,
        "peak_freq": round(float(peak_freq), 1),
        "low_ratio": round(float(np.sum(low) / total_energy), 4),
        "mid_ratio": round(float(np.sum(mid) / total_energy), 4),
        "high_ratio": round(float(np.sum(high) / total_energy), 4),
    }

def main():
    force = "--force" in sys.argv
    done = set() if force else load_done_files()
    if force:
        print("【强制模式】将重新计算所有文件")

    os.makedirs(PLOT_DIR, exist_ok=True)
    new_rows = []
    for f in sorted(os.listdir(PROCESSED_DIR)):
        if not f.lower().endswith(".wav"):
            continue
        base = os.path.splitext(f)[0]
        if base in done and not force:
            continue
        feat = extract_feature(os.path.join(PROCESSED_DIR, f))
        if feat:
            new_rows.append(feat)
            # 画频谱图
            plt.figure(figsize=(8, 4))
            wav = os.path.join(PROCESSED_DIR, f)
            sr, data = wavfile.read(wav)
            if data.ndim > 1:
                data = data[:, 0]
            plt.plot(np.fft.rfftfreq(len(data), 1 / sr), np.abs(np.fft.rfft(data)))
            plt.title(base)
            plt.xlabel("频率 (Hz)")
            plt.ylabel("幅值")
            plt.xlim(0, 5000)
            plt.tight_layout()
            plt.savefig(os.path.join(PLOT_DIR, base + ".png"))
            plt.close()
            print(f"  [计算] {f}")

    if not new_rows:
        print("没有新文件需要计算")
    else:
        # 合并旧数据与新数据
        all_rows = []
        if os.path.isfile(FEATURE_CSV) and not force:
            with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
                all_rows = list(csv.DictReader(fp))
        all_rows.extend(new_rows)
        with open(FEATURE_CSV, "w", newline="", encoding="utf-8-sig") as fp:
            writer = csv.DictWriter(fp, fieldnames=["file", "sample_rate", "peak_freq", "low_ratio", "mid_ratio", "high_ratio"])
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"新增 {len(new_rows)} 条，总计 {len(all_rows)} 条 → {FEATURE_CSV}")

if __name__ == "__main__":
    main()