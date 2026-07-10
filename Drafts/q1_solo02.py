import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess


plt.rcParams['font.sans-serif'] = ['SimHei'] 

# 假设数据 DataFrame 名叫 df
file_path = r"C:\Users\MX\Downloads\C_attatchment_v3.csv"
df = pd.read_csv(file_path, encoding='cp936')

# 1. 定义 BMI 分组
bins = [20, 28, 32, 36, 40, 100]  # BMI 区间
labels = ["20-28", "28-32", "32-36", "36-40", "≥40"]
df["BMI_group"] = pd.cut(df["孕妇BMI"], bins=bins, labels=labels, right=False)

# 孕期分区线
early_end, mid_end = 12, 27

def add_trimester_lines(ax):
    """在图上添加早中晚孕分界线"""
    ax.axvline(x=early_end, color="red", linestyle="--", alpha=0.7, label="早期≤12")
    ax.axvline(x=mid_end, color="blue", linestyle="--", alpha=0.7, label="中期13-27")
    # 晚期≥28 直接由图右边界表示
    return ax

# ========================
# 图1：分 BMI 组 LOWESS 曲线
# ========================
plt.figure(figsize=(8, 6))
colors = sns.color_palette("tab10", len(labels))

for i, group in enumerate(labels):
    sub = df[df["BMI_group"] == group]
    if len(sub) > 10:  # 至少10个点再画
        smoothed = lowess(sub["Y染色体浓度"], sub["检测孕周小数（周）"], frac=0.3)
        plt.plot(smoothed[:, 0], smoothed[:, 1], color=colors[i], label=f"BMI {group}")

plt.scatter(df["检测孕周小数（周）"], df["Y染色体浓度"], alpha=0.2, color="gray", s=10)
plt.xlabel("孕周（周）")
plt.ylabel("Y染色体浓度")
plt.title("不同 BMI 分组的孕周-Y浓度趋势 (LOWESS)")
add_trimester_lines(plt.gca())
plt.legend()
plt.show()

# ========================
# 图2：颜色映射 BMI 的散点图
# ========================
plt.figure(figsize=(8, 6))
scatter = plt.scatter(df["检测孕周小数（周）"], df["Y染色体浓度"], 
                      c=df["孕妇BMI"], cmap="viridis", alpha=0.6)
plt.colorbar(scatter, label="BMI")
plt.xlabel("孕周（周）")
plt.ylabel("Y染色体浓度")
plt.title("孕周 vs Y浓度 （颜色表示BMI）")
add_trimester_lines(plt.gca())
plt.show()

# ========================
# 图3：FacetGrid 按 BMI 分面
# ========================
g = sns.FacetGrid(df, col="BMI_group", col_wrap=3, height=3.5, sharey=True)
g.map_dataframe(sns.scatterplot, x="检测孕周小数（周）", y="Y染色体浓度", alpha=0.5)

for ax in g.axes.flatten():
    add_trimester_lines(ax)

g.set_axis_labels("孕周（周）", "Y染色体浓度")
g.fig.suptitle("不同 BMI 分组的孕周-Y浓度散点图（含孕期分区）", y=1.02)
plt.show()