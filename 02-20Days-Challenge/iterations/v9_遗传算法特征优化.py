import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']   # ← 新增：中文支持
plt.rcParams['axes.unicode_minus'] = False      # ← 新增：负号正常显示

import pygad
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ========== 路径配置 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FEATURE_CSV = os.path.join(PROJECT_DIR, "ga_dataset", "features", "train_features.csv")
FIGURE_DIR = os.path.join(PROJECT_DIR, "ga_dataset", "figures")
os.makedirs(FIGURE_DIR, exist_ok=True)

# ========== 加载数据 ==========
df = pd.read_csv(FEATURE_CSV)
feature_cols = ["peak_freq", "low_ratio", "mid_ratio", "high_ratio"]
X_full = df[feature_cols].values
y_raw = df["label"].values

le = LabelEncoder()
y = le.fit_transform(y_raw)
print(f"📊 加载数据: {len(df)} 条, 特征数: {len(feature_cols)}")
print(f"🏷️  类别: {list(le.classes_)}\n")

# ========== 适应度函数 ==========
def fitness_func(ga_instance, solution, solution_idx):
    selected = solution.astype(bool)
    if not np.any(selected):
        return 0.0
    X_sel = X_full[:, selected]
    clf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=3)
    scores = cross_val_score(clf, X_sel, y, cv=5, scoring="accuracy")
    return float(scores.mean())

# ========== 遗传算法配置 ==========
num_features = len(feature_cols)
print("🧬 遗传算法配置:")
print(f"  特征数: {num_features}")
print(f"  种群大小: 8")
print(f"  进化代数: 20")
print(f"  突变率: 30%\n")

ga_instance = pygad.GA(
    num_generations=20,
    num_parents_mating=4,
    sol_per_pop=8,
    num_genes=num_features,
    gene_space=[0, 1],
    fitness_func=fitness_func,
    mutation_percent_genes=30,
    mutation_type="random",
    crossover_type="single_point",
    random_seed=42,
    suppress_warnings=True
)

# ========== 运行 ==========
print("🚀 开始进化...")
ga_instance.run()
print("✅ 进化完成！\n")

# ========== 解析最优解 ==========
best_solution, best_fitness, _ = ga_instance.best_solution()
selected_mask = best_solution.astype(bool)
selected_features = [feature_cols[i] for i, sel in enumerate(selected_mask) if sel]

print("=" * 60)
print("🏆 遗传算法最优结果")
print("=" * 60)
print(f"最优特征掩码: {best_solution.tolist()}")
print(f"选中特征: {selected_features}")
print(f"最佳CV准确率: {best_fitness:.4f}")

# ========== 对比实验 ==========
clf_full = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=3)
scores_full = cross_val_score(clf_full, X_full, y, cv=5, scoring="accuracy")

X_sel = X_full[:, selected_mask]
clf_sel = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=3)
scores_sel = cross_val_score(clf_sel, X_sel, y, cv=5, scoring="accuracy")

print(f"\n📊 对比实验 (5折CV):")
print(f"  全特征 ({len(feature_cols)}个): {scores_full.mean():.4f} (+/- {scores_full.std():.4f})")
print(f"  GA筛选 ({len(selected_features)}个): {scores_sel.mean():.4f} (+/- {scores_sel.std():.4f})")

# ========== 适应度曲线 ==========
plt.figure(figsize=(8, 5))
plt.plot(ga_instance.best_solutions_fitness, marker='o', color='#E74C3C', linewidth=2, markersize=4)
plt.xlabel("进化代数")
plt.ylabel("最佳适应度 (交叉验证准确率)")
plt.title("遗传算法特征选择 - 适应度进化曲线")
plt.grid(True, alpha=0.3)
plt.tight_layout()
curve_path = os.path.join(FIGURE_DIR, "ga_fitness_curve.png")
plt.savefig(curve_path, dpi=150)
plt.close()
print(f"\n✅ 适应度曲线已保存: {curve_path}")

# ========== 保存结果 ==========
best_feature_file = os.path.join(PROJECT_DIR, "ga_dataset", "features", "best_features.txt")
with open(best_feature_file, "w", encoding="utf-8") as f:
    f.write(f"=== 遗传算法特征选择结果 ===\n")
    f.write(f"最优特征掩码: {best_solution.tolist()}\n")
    f.write(f"选中特征: {selected_features}\n")
    f.write(f"最佳CV准确率: {best_fitness:.4f}\n")
    f.write(f"全特征CV准确率: {scores_full.mean():.4f} (+/- {scores_full.std():.4f})\n")
    f.write(f"筛选后CV准确率: {scores_sel.mean():.4f} (+/- {scores_sel.std():.4f})\n")
print(f"✅ 最优特征信息已保存: {best_feature_file}")

print("\n🎉 v9 全部完成！")