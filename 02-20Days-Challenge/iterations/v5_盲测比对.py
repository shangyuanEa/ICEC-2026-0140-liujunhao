import os
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

ANSWER_CSV = os.path.join(DATA_DIR, "盲测答案.csv")
RESULT_CSV = os.path.join(PROCESSED_DIR, "盲测结果.csv")


def load_answer(path):
    """读取答案表：文件名 -> 是否异常（'是'/'否'）"""
    mapping = {}
    with open(path, encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            # 兼容表头：文件名 / file
            fname = row.get("文件名") or row.get("file") or ""
            label = row.get("是否异常") or row.get("label") or ""
            mapping[fname.strip()] = label.strip()
    return mapping


def load_result(path):
    """读取盲测结果：文件名 -> 预测（'正常运行' / '异常-xxx'）"""
    mapping = {}
    with open(path, encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            fname = row.get("file") or ""
            pred = row.get("predict") or ""
            mapping[fname.strip()] = pred.strip()
    return mapping


def judge(answer_label, pred_text):
    """判断是否判对：
    - 答案'是'(异常)  -> 预测必须含'异常'
    - 答案'否'(正常)  -> 预测必须是'正常运行'
    """
    if answer_label == "是":
        return "异常" in pred_text
    elif answer_label == "否":
        return pred_text == "正常运行"
    return False


def main():
    if not os.path.isfile(ANSWER_CSV):
        print(f"找不到答案表：{ANSWER_CSV}")
        return
    if not os.path.isfile(RESULT_CSV):
        print(f"找不到盲测结果：{RESULT_CSV}，请先运行 v4_盲测.py")
        return

    answers = load_answer(ANSWER_CSV)
    results = load_result(RESULT_CSV)

    print("=" * 60)
    print("【盲测比对】逐条对照 盲测答案.csv vs 盲测结果.csv")
    print("=" * 60)
    print(f"{'文件名':<22}{'答案':<8}{'预测':<18}{'结果'}")
    print("-" * 60)

    total = 0
    correct = 0
    for fname, pred in sorted(results.items()):
        ans = answers.get(fname, "未收录")
        if ans in ("是", "否"):
            ok = judge(ans, pred)
            total += 1
            if ok:
                correct += 1
            mark = "✓ 正确" if ok else "✗ 错误"
        else:
            mark = f"? 答案表无此文件（{ans}）"
        print(f"{fname:<22}{ans:<8}{pred:<18}{mark}")

    print("-" * 60)
    if total > 0:
        acc = round(correct / total * 100, 1)
        print(f"总计：{correct}/{total} 正确，准确率 {acc}%")
    else:
        print("没有可比对的有效条目，请检查两个 CSV 的文件名是否一致。")
    print("=" * 60)


if __name__ == "__main__":
    main()