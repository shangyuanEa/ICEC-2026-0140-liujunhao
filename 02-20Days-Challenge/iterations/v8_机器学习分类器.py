import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']   # ← 新增：中文支持
plt.rcParams['axes.unicode_minus'] = False      # ← 新增：负号正常显示

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, classification_report,
                             ConfusionMatrixDisplay)

# ========== 路径配置 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FEATURE_CSV = os.path.join(PROJECT_DIR, "ga_dataset", "features", "train_features.csv")
FIGURE_DIR = os.path.join(PROJECT_DIR, "ga_dataset", "figures")
os.makedirs(FIGURE_DIR, exist_ok=True)

# ========== 加载数据 ==========
df = pd.read_csv(FEATURE_CSV)
print(f"📊 加载数据: {len(df)} 条样本")
print(f"📋 标签分布:\n{df['label'].value_counts()}\n")

feature_cols = ["peak_freq", "low_ratio", "mid_ratio", "high_ratio"]
X = df[feature_cols].values
y_raw = df["label"].values

# ========== 标签编码 ==========
le = LabelEncoder()
y = le.fit_transform(y_raw)
class_names = le.classes_
print(f"🏷️  编码映射: {dict(zip(class_names, range(len(class_names))))}\n")

# ========== 5折分层交叉验证 ==========
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ========== 决策树 ==========
print("=" * 60)
print("🌳 决策树 (Decision Tree, max_depth=5)")
print("=" * 60)
dt_accuracies = []
for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    clf = DecisionTreeClassifier(random_state=42, max_depth=5)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    acc = accuracy_score(y_test, pred)
    dt_accuracies.append(acc)
    print(f"  Fold {fold} 准确率: {acc:.3f}")
print(f"📈 决策树平均准确率: {np.mean(dt_accuracies):.3f} (+/- {np.std(dt_accuracies):.3f})")

# ========== 随机森林 ==========
print("\n" + "=" * 60)
print("🌲 随机森林 (Random Forest, 100棵树, max_depth=5)")
print("=" * 60)
rf_accuracies = []
rf_cms = []
for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    acc = accuracy_score(y_test, pred)
    rf_accuracies.append(acc)
    rf_cms.append(confusion_matrix(y_test, pred))
    print(f"  Fold {fold} 准确率: {acc:.3f}")
print(f"📈 随机森林平均准确率: {np.mean(rf_accuracies):.3f} (+/- {np.std(rf_accuracies):.3f})")

# ========== 平均混淆矩阵图 ==========
avg_cm = np.mean(rf_cms, axis=0)
disp = ConfusionMatrixDisplay(confusion_matrix=avg_cm, display_labels=class_names)
disp.plot(cmap="Blues", values_format=".1f")
plt.title("随机森林 - 平均混淆矩阵 (5折交叉验证)")
plt.tight_layout()
cm_path = os.path.join(FIGURE_DIR, "rf_confusion_matrix.png")
plt.savefig(cm_path, dpi=150)
plt.close()
print(f"\n✅ 混淆矩阵图已保存: {cm_path}")

# ========== 特征重要性图 ==========
rf_full = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
rf_full.fit(X, y)
importances = rf_full.feature_importances_

plt.figure(figsize=(8, 5))
colors = plt.cm.viridis(importances / max(importances))
bars = plt.bar(feature_cols, importances, color=colors)
plt.xlabel("特征")
plt.ylabel("重要性")
plt.title("随机森林特征重要性 (全数据训练)")
plt.xticks(rotation=15)
for bar, imp in zip(bars, importances):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
             f"{imp:.3f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
fi_path = os.path.join(FIGURE_DIR, "feature_importance.png")
plt.savefig(fi_path, dpi=150)
plt.close()
print(f"✅ 特征重要性图已保存: {fi_path}")

# ========== 决策树规则 ==========
dt_full = DecisionTreeClassifier(random_state=42, max_depth=3)
dt_full.fit(X, y)
tree_rules = export_text(dt_full, feature_names=feature_cols)
print("\n" + "=" * 60)
print("🌳 决策树规则 (深度=3):")
print("=" * 60)
print(tree_rules)

# ========== 保存结果摘要 ==========
summary_path = os.path.join(FIGURE_DIR, "v8_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"样本数: {len(df)}\n")
    f.write(f"标签分布:\n{df['label'].value_counts().to_string()}\n\n")
    f.write(f"决策树平均准确率: {np.mean(dt_accuracies):.4f} (+/- {np.std(dt_accuracies):.4f})\n")
    f.write(f"随机森林平均准确率: {np.mean(rf_accuracies):.4f} (+/- {np.std(rf_accuracies):.4f})\n\n")
    f.write("特征重要性:\n")
    for feat, imp in zip(feature_cols, importances):
        f.write(f"  {feat}: {imp:.4f}\n")
print(f"✅ 结果摘要已保存: {summary_path}")

print("\n🎉 v8 全部完成！")