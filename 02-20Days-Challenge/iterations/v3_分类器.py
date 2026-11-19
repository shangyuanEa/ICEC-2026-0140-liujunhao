import os
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
RESULT_CSV = os.path.join(PROCESSED_DIR, "分类结果.csv")

LABEL_KEYS = {
    "一档": "normal_speed1",
    "二档": "normal_speed2",
    "三档": "normal_speed3",
    "卡入异物": "foreign_paper",
    "进风口堵住": "intake_block",
}
ANOMALY_LABELS = {"foreign_paper", "intake_block"}
HIGH_THRESHOLD = 0.25
PEAK_MIN = 30.0
PEAK_MAX = 400.0


def true_label(filename):
    for k, v in LABEL_KEYS.items():
        if k in filename:
            return v
    return "unknown"


def predict(high_ratio, peak_freq):
    if high_ratio > HIGH_THRESHOLD and PEAK_MIN < peak_freq < PEAK_MAX:
        return "异常"
    return "正常"


def main():
    rows = []
    with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
        for row in csv.DictReader(fp):
            tl = true_label(row["file"])
            pred = predict(float(row["high_ratio"]), float(row["peak_freq"]))
            is_anomaly_true = tl in ANOMALY_LABELS
            correct = "是" if (pred == "异常") == is_anomaly_true else "否"
            rows.append({
                "file": row["file"],
                "true_label": tl,
                "predict": pred,
                "correct": correct,
            })

    total = len(rows)
    right = sum(1 for r in rows if r["correct"] == "是")
    acc = round(right / total * 100, 1) if total else 0.0

    with open(RESULT_CSV, "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=["file", "true_label", "predict", "correct"])
        w.writeheader()
        w.writerows(rows)

    print("分类完成:", right, "/", total, "准确率", acc, "% ->", RESULT_CSV)


if __name__ == "__main__":
    main()