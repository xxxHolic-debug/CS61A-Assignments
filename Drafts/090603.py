# -*- coding: utf-8 -*-
"""
混合效应模型分析（孕妇纵向数据）
适配小样本、中文显示、自动容错
"""

# ===== 环境准备 =====
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

import statsmodels.api as sm
from statsmodels.formula.api import mixedlm
from patsy import dmatrix
from scipy.stats import chi2

# 屏蔽无关紧要的警告
warnings.filterwarnings("ignore", message="omni_normtest is not valid")
warnings.filterwarnings("ignore", category=RuntimeWarning)

# 中文字体设置（自动适配）
plt.rcParams['axes.unicode_minus'] = False
for font in ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']:
    if font in plt.rcParams['font.sans-serif'] or plt.matplotlib.font_manager.findfont(font, fallback_to_default=False):
        plt.rcParams['font.sans-serif'] = [font]
        break

# ===== 读取与准备数据 =====
file_path = r"C:\Users\MX\Downloads\C_attatchment_v3.xlsx"
df_raw = pd.read_excel(file_path)

COL_SUBJ = "孕妇代码"
COL_Y    = "Y染色体浓度"
COL_GA   = "检测孕周小数（周）"
COL_BMI  = "孕妇BMI"

df = df_raw[[COL_SUBJ, COL_Y, COL_GA, COL_BMI]].copy()
df = df.dropna(subset=[COL_SUBJ, COL_Y, COL_GA, COL_BMI])
df = df[(df[COL_GA].between(5, 42)) & (df[COL_BMI].between(12, 50))]
df = df[df[COL_Y] >= 0]
df[COL_SUBJ] = df[COL_SUBJ].astype(str)

Y_VAR, GA_VAR, BMI_VAR = COL_Y, COL_GA, COL_BMI

print(f"孕妇数: {df[COL_SUBJ].nunique()} | 总记录数: {len(df)}")

# ===== 可视化 =====
# 每位孕妇的纵向散点
g = sns.FacetGrid(df, col=COL_SUBJ, col_wrap=6, height=2.2, sharex=True, sharey=False)
g.map_dataframe(sns.scatterplot, x=GA_VAR, y=Y_VAR, alpha=0.7, s=25)
g.set_axis_labels("孕周(周)", "Y染色体浓度")
g.fig.suptitle("各孕妇纵向散点", y=1.03)
plt.show()

# 群体层面散点+LOWESS
plt.figure(figsize=(6,4))
sns.scatterplot(data=df, x=GA_VAR, y=Y_VAR, hue=COL_SUBJ, legend=False, alpha=0.4)
sns.regplot(data=df, x=GA_VAR, y=Y_VAR, scatter=False, lowess=True, color="black")
plt.title("群体散点 + LOWESS平滑")
plt.show()

# ===== 混合效应模型 =====
formula = f"{Y_VAR} ~ {GA_VAR} + {BMI_VAR}"

# 随机截距模型
model_reml = mixedlm(formula, data=df, groups=df[COL_SUBJ])
res_reml = model_reml.fit(reml=True, method='lbfgs')
print("\n=== 随机截距模型 ===")
print(res_reml.summary())

# 随机截距 + 孕周斜率
exog_re = df[[GA_VAR]].copy()
exog_re["Intercept"] = 1.0
exog_re = exog_re[["Intercept", GA_VAR]]

model_rs = sm.MixedLM.from_formula(formula, groups=COL_SUBJ, exog_re=exog_re, data=df)
res_rs = model_rs.fit(reml=True, method='lbfgs')
print("\n=== 随机截距+斜率模型 ===")
print(res_rs.summary())

# 似然比检验
llf0, llf1 = res_reml.llf, res_rs.llf
lr_stat = 2 * (llf1 - llf0)
df_diff = res_rs.df_modelwc - res_reml.df_modelwc
p_value = chi2.sf(lr_stat, df_diff)
print(f"\n随机斜率 vs 截距-only: LR={lr_stat:.3f}, df={df_diff}, p={p_value:.4g}")

# ===== 样条非线性模型 =====
dm = dmatrix("bs(x, df=3, degree=3, include_intercept=False)", 
             {"x": df[GA_VAR]}, return_type="dataframe")
dm.columns = [f"ga_s{i+1}" for i in range(dm.shape[1])]
df_spline = pd.concat([df.reset_index(drop=True), dm.reset_index(drop=True)], axis=1)

spline_terms = " + ".join(dm.columns)
formula_spline = f"{Y_VAR} ~ {spline_terms} + {BMI_VAR}"

model_spline_ml = mixedlm(formula_spline, data=df_spline, groups=df_spline[COL_SUBJ])
res_spline_ml = model_spline_ml.fit(reml=False, method='lbfgs')

model_lin_ml = mixedlm(formula, data=df, groups=df[COL_SUBJ])
res_lin_ml = model_lin_ml.fit(reml=False, method='lbfgs')

llf0, llf1 = res_lin_ml.llf, res_spline_ml.llf
lr_stat = 2*(llf1 - llf0)
df_diff = res_spline_ml.df_modelwc - res_lin_ml.df_modelwc
p_value = chi2.sf(lr_stat, df_diff)
print(f"\n线性 vs 样条: LR={lr_stat:.3f}, df={df_diff}, p={p_value:.4g}")

# ===== 固定效应结果 =====
print("\n固定效应系数：")
print(res_reml.fe_params)
print("95% CI：")
print(res_reml.conf_int())

# ===== 残差诊断 =====
df["fitted"] = res_reml.fittedvalues
df["resid"] = df[Y_VAR] - df["fitted"]

plt.figure(figsize=(6,4))
sns.scatterplot(data=df, x="fitted", y="resid", alpha=0.5)
plt.axhline(0, color='red', ls='--')
plt.title("残差 vs 拟合值")
plt.show()

sm.qqplot(df["resid"], line='45', fit=True)
plt.title("残差QQ图")
plt.show()

# ===== 边际效应曲线 =====
ga_grid = np.linspace(df[GA_VAR].min(), df[GA_VAR].max(), 100)
bmi_ref = df[BMI_VAR].median()
pred_df = pd.DataFrame({GA_VAR: ga_grid, BMI_VAR: bmi_ref})
pred_df["_group"] = df[COL_SUBJ].iloc[0]
pred = res_reml.predict(exog=pred_df, exog_re=np.zeros((len(pred_df), 1)))

plt.figure(figsize=(6,4))
sns.scatterplot(data=df, x=GA_VAR, y=Y_VAR, alpha=0.3)
plt.plot(ga_grid, pred, color='black', lw=2, label='孕周边际效应')
plt.legend()
plt.show()
