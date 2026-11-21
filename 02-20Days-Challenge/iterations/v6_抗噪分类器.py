import os
import csv
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
NOISE_CSV = os.path.join(PROCESSED_DIR, "抗噪结果.csv")

# 分层判据（与 v4 一致）
PEAK_BLOCK = 100
PEAK_NORMAL = 95
HIGH_ABNORMAL = 0.22

def get_true_label(filename):
    if "异物" in filename or "堵" in filename or "盲侧" in filename:
        return "异常"
    return "正常"

def predict(peak, high):
    if peak > PEAK_BLOCK:
        return "异常-进风口堵塞"
    if peak < PEAK_NORMAL and high > HIGH_ABNORMAL:
        return "异常-卡入异物"
    return "正常运行"

def main():
    print("=" * 60)
    print("【抗噪测试】对比正常样本与带背景噪声样本的分类表现")
    print("=" * 60)

    rows = []
    with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
        for row in csv.DictReader(fp):
            fname = row["file"]
            is_noise = fname.startswith("抗噪_")
            peak = float(row["peak_freq"])
            high = float(row["high_ratio"])
            pred = predict(peak, high)
            true_type = get_true_label(fname)
            is_abnormal = "异常" in pred
            correct = "是" if (is_abnormal) == (true_type == "异常") else "否"
            rows.append({
                "file": fname,
                "has_noise": "是" if is_noise else "否",
                "peak_freq": peak,
                "high_ratio": high,
                "predict": pred,
                "true_type": true_type,
                "correct": correct,
            })
            tag = "🔊抗噪" if is_noise else "🔇干净"
            print(f"  {tag} {fname:20s} | 主频{peak:6.1f} | 高频{high:.3f} | {pred} | {'✓' if correct=='是' else '✗'}")

    with open(NOISE_CSV, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=["file", "has_noise", "peak_freq", "high_ratio", "predict", "true_type", "correct"])
        writer.writeheader()
        writer.writerows(rows)

    # 统计
    clean = [r for r in rows if r["has_noise"] == "否"]
    noisy = [r for r in rows if r["has_noise"] == "是"]
    clean_acc = sum(1 for r in clean if r["correct"] == "是") / len(clean) * 100 if clean else 0
    noisy_acc = sum(1 for r in noisy if r["correct"] == "是") / len(noisy) * 100 if noisy else 0
    print("=" * 60)
    print(f"干净样本：{sum(1 for r in clean if r['correct']=='是')}/{len(clean)} 正确，准确率 {clean_acc:.0f}%")
    print(f"抗噪样本：{sum(1 for r in noisy if r['correct']=='是')}/{len(noisy)} 正确，准确率 {noisy_acc:.0f}%")
    print("=" * 60)
    print(f"结果已保存：{NOISE_CSV}")

if __name__ == "__main__":
    main()