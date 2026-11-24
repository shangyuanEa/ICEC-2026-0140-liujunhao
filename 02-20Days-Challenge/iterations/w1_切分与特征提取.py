import os
import re
import csv
import sys
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ========== 路径配置（基于脚本位置自动定位） ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(PROJECT_DIR, "data", "raw", "决策树训练数据")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
GA_FEATURES_DIR = os.path.join(PROJECT_DIR, "ga_dataset", "features")
PLOT_DIR = os.path.join(PROCESSED_DIR, "频谱图")

# 创建目录
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(GA_FEATURES_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# ========== 参数 ==========
STATE_MAP = {"1": "一档", "2": "二档", "3": "三档", "4": "堵进风口", "5": "异物"}
SEGMENT_SEC = 15
TOTAL_SEGMENTS = 12
SAMPLE_RATE = 44100

# ========== 特征提取函数（复用你的 v2 逻辑） ==========
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

# ========== 主流程 ==========
def main():
    force = "--force" in sys.argv
    plot = "--plot" in sys.argv
    print(f"{'='*60}")
    print(f"🎯 w1_切分与特征提取.py")
    print(f"📥 输入: {INPUT_DIR}")
    print(f"📤 wav输出: {PROCESSED_DIR}")
    print(f"📤 特征输出: {GA_FEATURES_DIR}")
    print(f"{'='*60}\n")

    # ---- 第一步：切分 m4a → 15秒 wav ----
    for fname in sorted(os.listdir(INPUT_DIR)):
        if not fname.lower().endswith(".m4a"):
            continue
        base = os.path.splitext(fname)[0]
        match = re.search(r'_(\d+)$', base)
        if not match:
            print(f"[跳过] 无法从 {fname} 提取状态数字")
            continue
        state = match.group(1)
        label = STATE_MAP.get(state, state)
        print(f"[切分] {fname} → 状态 {state}({label})")

        audio = AudioSegment.from_file(os.path.join(INPUT_DIR, fname), format="m4a")
        audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1)

        max_possible = len(audio) // (SEGMENT_SEC * 1000)
        actual = min(TOTAL_SEGMENTS, max_possible)
        if actual < TOTAL_SEGMENTS:
            print(f"  ⚠️  只够切 {actual} 段")

        for i in range(actual):
            out_name = f"训练样本_{state}.{i+1}.wav"
            out_path = os.path.join(PROCESSED_DIR, out_name)
            if os.path.isfile(out_path) and not force:
                continue
            segment = audio[i*SEGMENT_SEC*1000 : (i+1)*SEGMENT_SEC*1000]
            segment.export(out_path, format="wav", parameters=["-acodec", "pcm_s16le"])

    # ---- 第二步：从 wav 提取特征 ----
    all_features = []
    for f in sorted(os.listdir(PROCESSED_DIR)):
        if not f.lower().endswith(".wav") or not f.startswith("训练样本_"):
            continue
        wav_path = os.path.join(PROCESSED_DIR, f)
        feat = extract_feature(wav_path)
        if not feat:
            continue
        # 解析标签
        state = f.split("_")[1].split(".")[0]
        feat["label"] = STATE_MAP.get(state, state)
        all_features.append(feat)

        # 可选：画频谱图
        if plot:
            plt.figure(figsize=(8, 4))
            sr, data = wavfile.read(wav_path)
            if data.ndim > 1:
                data = data[:, 0]
            plt.plot(np.fft.rfftfreq(len(data), 1 / sr), np.abs(np.fft.rfft(data)))
            plt.title(feat["file"])
            plt.xlabel("频率 (Hz)")
            plt.ylabel("幅值")
            plt.xlim(0, 5000)
            plt.tight_layout()
            plt.savefig(os.path.join(PLOT_DIR, feat["file"] + ".png"))
            plt.close()

        print(f"  [特征] {f} → {feat['label']}")

    # ---- 第三步：写入 ga_dataset/features/train_features.csv ----
    if all_features:
        csv_path = os.path.join(GA_FEATURES_DIR, "train_features.csv")
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as fp:
            fieldnames = ["file", "sample_rate", "peak_freq", "low_ratio", "mid_ratio", "high_ratio", "label"]
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_features)
        print(f"\n✅ 完成！共 {len(all_features)} 条，已保存至:")
        print(f"   {csv_path}")
    else:
        print("❌ 未提取到任何特征")

if __name__ == "__main__":
    main()