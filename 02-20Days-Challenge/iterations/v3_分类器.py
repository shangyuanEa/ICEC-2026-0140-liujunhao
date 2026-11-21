import os
import csv
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FEATURE_CSV = os.path.join(PROCESSED_DIR, "特征汇总.csv")
RESULT_CSV = os.path.join(PROCESSED_DIR, "分类结果.csv")
LABEL_MAP = os.path.join(PROJECT_DIR, "data", "label_map.csv")

# 分层判据
PEAK_BLOCK = 100
PEAK_NORMAL = 95
HIGH_ABNORMAL = 0.22

def load_label_map():
    labels = {}
    if os.path.isfile(LABEL_MAP):
        with open(LABEL_MAP, encoding="utf-8-sig") as fp:
            for row in csv.DictReader(fp):
                labels[row["file"]] = row
    return labels

def load_done_files():
    """读已有分类结果，返回已处理过的文件名集合"""
    done = set()
    if os.path.isfile(RESULT_CSV):
        with open(RESULT_CSV, encoding="utf-8-sig") as fp:
            for row in csv.DictReader(fp):
                done.add(row["file"])
    return done

def predict(peak, high):
    if peak > PEAK_BLOCK:
        return "异常"
    if peak < PEAK_NORMAL and high > HIGH_ABNORMAL:
        return "异常"
    return "正常"

def main():
    force = "--force" in sys.argv
    done = set() if force else load_done_files()
    if force:
        print("【强制模式】将重新分类所有文件")

    if not os.path.isfile(FEATURE_CSV):
        print("错误：找不到 特征汇总.csv，请先运行 v2")
        return

    labels = load_label_map()
    new_rows = []

    with open(FEATURE_CSV, encoding="utf-8-sig") as fp:
        for row in csv.DictReader(fp):
            fname = row["file"]
            if fname in done and not force:
                continue
            peak = float(row["peak_freq"])
            high = float(row["high_ratio"])
            pred = predict(peak, high)

            # 查标签
            true_label = "unknown"
            if fname in labels:
                true_label = labels[fname].get("工况类别", "unknown")
            elif "异物" in fname or "堵" in fname or "盲侧" in fname:
                true_label = "异常"
            elif "一档" in fname or "二档" in fname or "三档" in fname:
                true_label = "正常"

            is_abnormal = "异常" in pred
            is_true_abnormal = true_label == "异常"
            correct = "是" if is_abnormal == is_true_abnormal else "否"

            new_rows.append({
                "file": fname,
                "true_label": true_label,
                "predict": pred,
                "correct": correct,
            })
            tag = "[新增]" if fname in done else "[计算]"
            print(f"  {tag} {fname:25s} | 预测:{pred:8s} | 实际:{true_label:6s} | {'✓' if correct=='是' else '✗'}")

    if not new_rows:
        print("没有新文件需要分类")
    else:
        # 合并旧数据
        all_rows = []
        if os.path.isfile(RESULT_CSV) and not force:
            with open(RESULT_CSV, encoding="utf-8-sig") as fp:
                all_rows = list(csv.DictReader(fp))
        all_rows.extend(new_rows)

        with open(RESULT_CSV, "w", newline="", encoding="utf-8-sig") as fp:
            writer = csv.DictWriter(fp, fieldnames=["file", "true_label", "predict", "correct"])
            writer.writeheader()
            writer.writerows(all_rows)

        correct_count = sum(1 for r in all_rows if r["correct"] == "是")
        print(f"新增 {len(new_rows)} 条，总计 {len(all_rows)} 条，正确 {correct_count} 条 → {RESULT_CSV}")

if __name__ == "__main__":
    main()