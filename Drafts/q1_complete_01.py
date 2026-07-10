# “读取数据 → 描述统计 → 混合效应回归 → 预测曲线 → 计算最佳检测时点”

import pandas as pd
import researchpy as rp
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import chardet

# 1. 自动检测编码并读取数据
with open(r"C:\Users\MX\Downloads\C_attatchment_v3.csv", 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

df = pd.read_csv(r"C:\Users\MX\Downloads\C_attatchment_v3.csv", encoding=encoding, sep="\t")

# 2. 数据概览
print(df.info())
rp.codebook(df)

# 3. 分组描述统计
print(rp.summary_cont(df.groupby(["孕妇BMI", "检测孕周小数（周）"])["Y染色体浓度"]))

# 4. 混合效应模型
# 假设 df 中有 "孕妇ID" 列作为随机效应分组变量
# 固定效应：BMI + 孕周
# 随机效应：孕妇ID（截距随机）
model = smf.mixedlm(
    "Y染色体浓度 ~ 孕妇BMI + 检测孕周小数（周） + 孕妇BMI:检测孕周小数（周）",
    data=df,
    groups=df["孕妇ID"]
)
result = model.fit()
print(result.summary())

# 5. 预测曲线
# 生成预测数据（不同BMI组，不同孕周）
bmi_values = sorted(df["孕妇BMI"].unique())
week_range = np.linspace(df["检测孕周小数（周）"].min(), df["检测孕周小数（周）"].max(), 100)

pred_df = pd.DataFrame([
    {"孕妇BMI": bmi, "检测孕周小数（周）": week, "孕妇ID": "new"}
    for bmi in bmi_values
    for week in week_range
])

pred_df["预测Y浓度"] = result.predict(pred_df)

# 绘图
plt.figure(figsize=(8,6))
sns.lineplot(data=pred_df, x="检测孕周小数（周）", y="预测Y浓度", hue="孕妇BMI", palette="tab10")
plt.axhline(4, color="red", linestyle="--", label="4% 阈值")
plt.legend()
plt.title("不同BMI组的Y染色体浓度预测曲线")
plt.show()

# 6. 计算最佳检测时点（预测浓度首次达到4%的孕周）
def get_best_week(pred_df, bmi):
    sub = pred_df[pred_df["孕妇BMI"] == bmi]
    reached = sub[sub["预测Y浓度"] >= 4]
    if not reached.empty:
        return reached.iloc[0]["检测孕周小数（周）"]
    else:
        return None

best_weeks = {bmi: get_best_week(pred_df, bmi) for bmi in bmi_values}
print("不同BMI组的最佳检测孕周（点估计）：", best_weeks)


# 7. Bootstrap 置信区间
n_boot = 500  # Bootstrap次数
ci_results = {bmi: [] for bmi in bmi_values}

for i in range(n_boot):
    # 有放回抽样
    sample_df = df.sample(frac=1, replace=True)
    try:
        boot_model = smf.mixedlm(
            "Y染色体浓度 ~ 孕妇BMI + 检测孕周小数（周） + 孕妇BMI:检测孕周小数（周）",
            data=sample_df,
            groups=sample_df["孕妇ID"]
        ).fit()
        
        boot_pred = pd.DataFrame([
            {"孕妇BMI": bmi, "检测孕周小数（周）": week, "孕妇ID": "new"}
            for bmi in bmi_values
            for week in week_range
        ])
        boot_pred["预测Y浓度"] = boot_model.predict(boot_pred)
        
        for bmi in bmi_values:
            week_val = get_best_week(boot_pred, bmi)
            if week_val:
                ci_results[bmi].append(week_val)
    except:
        continue  # 避免拟合失败中断

# 8. 计算95%置信区间
ci_summary = {}
for bmi in bmi_values:
    if ci_results[bmi]:
        lower = np.percentile(ci_results[bmi], 2.5)
        upper = np.percentile(ci_results[bmi], 97.5)
        ci_summary[bmi] = (best_weeks[bmi], lower, upper)
    else:
        ci_summary[bmi] = (best_weeks[bmi], None, None)

print("\n不同BMI组最佳检测孕周及95%置信区间：")
for bmi, (est, low, up) in ci_summary.items():
    if low and up:
        print(f"BMI={bmi}: {est:.2f} 周 (95% CI: {low:.2f} ~ {up:.2f})")
    else:
        print(f"BMI={bmi}: {est} 周 (CI无法计算)")