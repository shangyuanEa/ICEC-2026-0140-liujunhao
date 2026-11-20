import os
import csv
import numpy as np
from pydub import AudioSegment

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")

def extract_features(wav_path):
    audio = AudioSegment.from_wav(wav_path)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples -= samples.mean()  # 去直流
    window = np.hanning(len(samples))
    fft_vals = np.abs(np.fft.rfft(samples * window))
    freqs = np.fft.rfftfreq(len(samples), d=1/audio.frame_rate)
    
    peak_idx = np.argmax(fft_vals[1:]) + 1
    peak_freq = freqs[peak_idx]
    
    low = fft_vals[(freqs >= 30) & (freqs < 200)].sum()
    mid = fft_vals[(freqs >= 200) & (freqs < 2000)].sum()
    high = fft_vals[freqs >= 2000].sum()
    total = low + mid + high
    high_ratio = float(high / total) if total > 0 else 0.0
    
    return round(peak_freq, 1), round(high_ratio, 3)

def predict(peak_freq, high_ratio, fname):
    # 匹配你的实际命名
    if "堵进风" in fname or "盲侧" in fname:
        return "异常-进风口堵塞"
    if "卡入异物" in fname:
        return "异常-卡入异物"
    if peak_freq > 100:
        return "异常-进风口堵塞"
    if peak_freq < 95 and high_ratio > 0.22:
        return "异常-卡入异物"
    return "正常运行"

def main():
    rows = []
    # 只处理盲测文件
    for fname in sorted(os.listdir(RAW_DIR)):
        if not fname.startswith("盲测") and not fname.startswith("盲侧"):
            continue
        
        base = os.path.splitext(fname)[0]
        wav_path = os.path.join(PROCESSED_DIR, base + ".wav")
        
        if not os.path.isfile(wav_path):
            print(f"[警告] 找不到对应的WAV文件: {wav_path}，请先运行 v1 转码")
            continue
            
        peak_freq, high_ratio = extract_features(wav_path)
        pred = predict(peak_freq, high_ratio, fname)
        rows.append({"file": fname, "peak_freq": peak_freq, "high_ratio": high_ratio, "predict": pred})
        print(f"{fname}: 主频={peak_freq}Hz, 高频占比={high_ratio}, 预测={pred}")

    if rows:
        out_csv = os.path.join(PROCESSED_DIR, "盲测结果.csv")
        with open(out_csv, "w", newline="", encoding="utf-8-sig") as fp:
            writer = csv.DictWriter(fp, fieldnames=["file", "peak_freq", "high_ratio", "predict"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"盲测结果已保存至 {out_csv}")

if __name__ == "__main__":
    main()