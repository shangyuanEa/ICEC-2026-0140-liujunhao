# -*- coding: utf-8 -*-
"""
人工和AI批量随机生成用户密码耗时.py
真实人工输入 + AI生成，修复AI耗时过短导致除零报错，确保表格导出
"""
import os
import re
import time
import random
import string
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_LENGTH = 12

HEADER_FILL = PatternFill(start_color="C9DAF8", end_color="C9DAF8", fill_type="solid")
YELLOW = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
GREEN = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def ask_int(prompt, default=10):
    while True:
        s = input(prompt).strip()
        if not s:
            return default
        if s.isdigit() and int(s) > 0:
            return int(s)
        print("  请输入正整数。")


def ask_yes_no(prompt, default=True):
    while True:
        s = input(prompt).strip().lower()
        if not s:
            return default
        if s in ("y", "yes", "是", "1"):
            return True
        if s in ("n", "no", "否", "0"):
            return False
        print("  请输入 y 或 n。")


def validate_account(acc):
    return bool(re.fullmatch(r"[A-Za-z]+", acc))


def validate_password(pwd):
    if len(pwd) != PASSWORD_LENGTH:
        return False, f"长度必须为 {PASSWORD_LENGTH} 位"
    if not re.search(r"[A-Z]", pwd):
        return False, "缺少大写字母"
    if not re.search(r"[a-z]", pwd):
        return False, "缺少小写字母"
    if not re.search(r"[0-9]", pwd):
        return False, "缺少数字"
    if not re.fullmatch(r"[A-Za-z0-9]+", pwd):
        return False, "只能包含英文字母和数字"
    return True, ""


def make_pwd(length=PASSWORD_LENGTH):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    pwd = [random.choice(string.ascii_uppercase),
           random.choice(string.ascii_lowercase),
           random.choice(string.digits)]
    pwd += [random.choice(chars) for _ in range(length - 3)]
    random.shuffle(pwd)
    return "".join(pwd)


def human_input(n):
    print("\n" + "=" * 50)
    print(f"人工输入模式：请依次输入 {n} 组「账号 + 密码」")
    print(f"要求：账号纯英文字母；密码 {PASSWORD_LENGTH} 位，含大写+小写+数字")
    print("=" * 50)
    input("准备好后按回车开始计时...")

    start = time.time()
    pairs = []
    for i in range(1, n + 1):
        while True:
            acc = input(f"[{i}/{n}] 账号: ").strip()
            if validate_account(acc):
                break
            print("  账号只能包含英文字母，请重新输入。")
        while True:
            pwd = input(f"[{i}/{n}] 密码: ").strip()
            ok, msg = validate_password(pwd)
            if ok:
                break
            print(f"  {msg}，请重新输入。")
        pairs.append((acc, pwd))

    elapsed = time.time() - start
    print(f"\n人工输入完成，耗时: {elapsed:.2f} 秒")
    return pairs, elapsed


def ai_generate(n):
    print("\n" + "=" * 50)
    print(f"AI 生成模式：生成 {n} 组账号密码")
    print("=" * 50)
    start = time.time()
    pairs = [(f"user{i:02d}", make_pwd()) for i in range(1, n + 1)]
    elapsed = time.time() - start
    for acc, pwd in pairs:
        print(f"  {acc}  {pwd}")
    print(f"\nAI 生成完成，耗时: {elapsed:.4f} 秒")
    return pairs, elapsed


def save_excel(human_pairs, human_time, ai_pairs, ai_time, count):
    if not ask_yes_no("\n是否输出为 Excel 表格？(y/n，默认 y): ", True):
        return

    path = input("请输入保存目录（直接回车则保存到当前目录）: ").strip()
    if not path:
        path = SCRIPT_DIR
    elif not os.path.isdir(path):
        print(f"目录不存在：{path}，改为保存到当前目录。")
        path = SCRIPT_DIR

    filename = "人工和AI批量随机生成用户密码耗时.xlsx"
    full_path = os.path.join(path, filename)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "账号密码耗时对比"

    ws.merge_cells("A1:F1")
    ws["A1"] = "人工 vs AI 批量随机生成用户密码耗时对比"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    headers = ["序号", "人工账号", "人工密码", "AI账号", "AI密码", "备注"]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center")
        c.border = BORDER

    for i in range(count):
        row = i + 3
        ws.cell(row=row, column=1, value=i + 1).alignment = Alignment(horizontal="center")
        if i < len(human_pairs):
            ws.cell(row=row, column=2, value=human_pairs[i][0]).fill = YELLOW
            ws.cell(row=row, column=3, value=human_pairs[i][1]).fill = YELLOW
        if i < len(ai_pairs):
            ws.cell(row=row, column=4, value=ai_pairs[i][0]).fill = GREEN
            ws.cell(row=row, column=5, value=ai_pairs[i][1]).fill = GREEN
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = BORDER

    start_row = count + 4
    ws.cell(row=start_row, column=1, value="方式").font = Font(bold=True)
    ws.cell(row=start_row, column=2, value="耗时（秒）").font = Font(bold=True)
    ws.cell(row=start_row + 1, column=1, value="人工")
    ws.cell(row=start_row + 1, column=2, value=round(human_time, 2))
    ws.cell(row=start_row + 2, column=1, value="AI")
    ws.cell(row=start_row + 2, column=2, value=round(ai_time, 4))

    # 修复除零：AI耗时过短时用高精度或标注
    if ai_time > 0:
        ws.cell(row=start_row + 3, column=1, value="提速比")
        ws.cell(row=start_row + 3, column=2, value=round(human_time / ai_time, 1))
    else:
        ws.cell(row=start_row + 3, column=1, value="提速比")
        ws.cell(row=start_row + 3, column=2, value="AI耗时极短(<0.0001s)，无法计算")

    for col, w in zip("ABCDEF", [6, 16, 18, 16, 18, 10]):
        ws.column_dimensions[col].width = w

    wb.save(full_path)
    print(f"\n表格已保存: {full_path}")


def main():
    print("=" * 50)
    print("   人工和AI批量随机生成用户密码耗时")
    print("=" * 50)

    count = ask_int("请输入要生成的密码数量（默认 10）: ", 10)
    compare = ask_yes_no("是否进行人工 vs AI 对比？(y/n，默认 y): ", True)

    human_pairs, human_time = [], 0.0
    if compare:
        human_pairs, human_time = human_input(count)

    ai_pairs, ai_time = ai_generate(count)

    print("\n" + "=" * 50)
    print("耗时对比结果")
    print("=" * 50)
    if compare and human_time > 0:
        print(f"  人工耗时: {human_time:.2f} 秒")
        print(f"  AI 耗时:  {ai_time:.4f} 秒")
        if ai_time > 0:
            print(f"  提速比:   {human_time / ai_time:.1f} 倍")
        else:
            print("  提速比:   AI耗时极短(<0.0001s)，无法计算")
    else:
        print(f"  AI 耗时: {ai_time:.4f} 秒")

    save_excel(human_pairs, human_time, ai_pairs, ai_time, count)
    print("\n全部完成。")


if __name__ == "__main__":
    main()