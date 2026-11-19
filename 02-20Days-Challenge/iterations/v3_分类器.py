import os
import csv

# 基于脚本所在目录算绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
RESULT_CSV = os.path.join(PROCESSED_DIR, "分类结果.csv")

LABEL_MAP = {
    "一档": "normal_speed1",
    "二档": "normal_speed2",
    "三档": "normal_speed3",
    "卡入异物": "foreign_paper",
    "进风口堵住": "intake_block",
}

def get_true_label(filename):
    for key, label in LABEL_MAP.items():
        if key in filename:
            return label
    return "unknown"

def classify(row):
    high = float(row["high_ratio"])
    peak = float(row["peak_freq"])
    if high > 0.25 and 30 < peak < 400:
        return "异常"
    return "正常"

def main():
    rows = []
    with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            true_label = get_true_label(row["file"])
            pred = classify(row)
            correct = "是" if (pred == "异常") == (true_label in ("foreign_paper", "intake_block")) else "否"
            rows.append({
                "file": row["file"],
                "true_label": true_label,
                "predict": pred,
                "correct": correct,
            })
    total = len(rows)
    right = sum(1 for r in rows if r["correct"] == "是")
    acc = round(right / total * 100, 1) if total else 0
    with open(RESULT_CSV, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=["file", "true_label", "predict", "correct"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"分类完成：{right}/{total}，准确率 {acc}%")
    print("结果已保存至", RESULT_CSV)

if __name__ == "__main__":
    main()