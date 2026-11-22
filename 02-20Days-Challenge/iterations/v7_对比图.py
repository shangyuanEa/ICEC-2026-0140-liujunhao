import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
PLOT_DIR = os.path.join(PROCESSED_DIR, "频谱图")

def load_features():
    path = os.path.join(PROCESSED_DIR, "特征汇总.csv")
    rows = []
    with open(path, encoding="utf-8-sig") as fp:
        for r in csv.DictReader(fp):
            rows.append(r)
    return rows

def plot_freq_compare(rows):
    normal = []
    abnormal = []
    for r in rows:
        if r["file"].startswith("抗噪_"):
            continue
        peak = float(r["peak_freq"])
        if "异物" in r["file"] or "堵" in r["file"] or "盲侧" in r["file"]:
            abnormal.append(peak)
        else:
            normal.append(peak)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([normal, abnormal])
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["正常工况", "异常工况"])
    ax.set_ylabel("主频 (Hz)")
    ax.set_title("正常 vs 异常工况 主频分布")
    ax.grid(True, alpha=0.3)
    out = os.path.join(PLOT_DIR, "对比_主频.png")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    print(f"已保存: {out}")

def plot_high_ratio(rows):
    labels = ["干净-正常", "干净-异常", "抗噪-正常", "抗噪-异常"]
    groups = {k: [] for k in labels}
    for r in rows:
        high = float(r["high_ratio"])
        is_noise = r["file"].startswith("抗噪_")
        is_abnormal = "异物" in r["file"] or "堵" in r["file"] or "盲侧" in r["file"]
        if is_noise and not is_abnormal:
            groups["抗噪-正常"].append(high)
        elif is_noise and is_abnormal:
            groups["抗噪-异常"].append(high)
        elif not is_noise and not is_abnormal:
            groups["干净-正常"].append(high)
        else:
            groups["干净-异常"].append(high)

    fig, ax = plt.subplots(figsize=(9, 5))
    pos = np.arange(1, len(labels) + 1)
    data = [groups[k] for k in labels]
    ax.boxplot(data, positions=pos, widths=0.6)
    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel("高频能量占比")
    ax.set_title("各工况组 高频能量占比对比")
    ax.grid(True, alpha=0.3)
    out = os.path.join(PLOT_DIR, "对比_高频占比.png")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    print(f"已保存: {out}")

def main():
    os.makedirs(PLOT_DIR, exist_ok=True)
    rows = load_features()
    plot_freq_compare(rows)
    plot_high_ratio(rows)
    print("对比图生成完毕")

if __name__ == "__main__":
    main()