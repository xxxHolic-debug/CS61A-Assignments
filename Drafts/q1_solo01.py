"""
单体纵向分析：单一孕妇随时间的变化

筛选：选择进行了多次不同日期检查的孕妇数据

绘图：绘制每位孕妇Y染色体浓度随孕周变化的三维图，x,y,z轴分别为 孕妇代号、孕周、Y染色体浓度

回归分析：对每位孕妇的数据进行线性/非线性回归，建立Y染色体浓度与孕周和BMI之间的关系模型

显著性检验：对每个模型的回归系数进行T-检验，检验孕周和BMI对Y染色体浓度的影响是否显著
"""


import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the data
file_path = r"C:\Users\MX\Downloads\C_attatchment_v3.csv"
df = pd.read_csv(file_path, encoding='cp936')

# Convert necessary columns to numeric and filter out NaNs
df['检测孕周小数（周）'] = pd.to_numeric(df['检测孕周小数（周）'], errors='coerce')
df['孕妇BMI'] = pd.to_numeric(df['孕妇BMI'], errors='coerce')
df['Y染色体浓度'] = pd.to_numeric(df['Y染色体浓度'], errors='coerce')
df['孕妇代号'] = df['孕妇代码']
df.dropna(subset=['检测孕周小数（周）', '孕妇BMI', 'Y染色体浓度', '孕妇代号'], inplace=True)

# Filter for pregnant women with multiple unique test dates
multi_visit_patients = df.groupby('孕妇代号')['检测日期'].nunique()
multi_visit_patients = multi_visit_patients[multi_visit_patients > 1].index

# Filter the main DataFrame to only include multi-visit patients
df_filtered = df[df['孕妇代号'].isin(multi_visit_patients)].copy()

# Map pregnant woman codes to numerical values for the plot
df_filtered['孕妇代号_数值'] = pd.factorize(df_filtered['孕妇代号'])[0]

# 1. 3D Plotting (Remains the same as before)
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(df_filtered['孕妇代号_数值'], df_filtered['检测孕周小数（周）'], df_filtered['Y染色体浓度'])

# Set labels for the axes
ax.set_xlabel('孕妇代号')
ax.set_ylabel('检测孕周小数（周）')
ax.set_zlabel('Y染色体浓度')
ax.set_title('Y染色体浓度随孕周和孕妇代号变化的三维散点图')

# Map numerical x-ticks back to pregnant woman codes
tick_positions = df_filtered['孕妇代号_数值'].unique()
tick_labels = df_filtered.groupby('孕妇代号_数值')['孕妇代号'].first().loc[tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=45, ha='right')

# Save the plot
plt.tight_layout()
plt.savefig(r'C:\Users\MX\Downloads\3D_Y_concentration_plot.png')
plt.close(fig)

# 2. Regression Analysis and Significance Testing for each individual
# Open a text file to save the regression results
with open(r'C:\Users\MX\Downloads\regression_results.txt', 'w', encoding='utf-8') as f:
    for patient_code in multi_visit_patients:
        patient_df = df_filtered[df_filtered['孕妇代号'] == patient_code].copy()

        # Check if there are enough observations for regression
        if len(patient_df) < 3:
            f.write(f"对孕妇 {patient_code} 的回归分析跳过：数据点少于3个，无法进行多元回归。\n")
            f.write("-" * 50 + "\n")
            continue

        # Define independent (X) and dependent (y) variables for regression
        X = patient_df[['孕妇BMI', '检测孕周小数（周）']]
        y = patient_df['Y染色体浓度']

        # Add a constant for the intercept term of the model
        X = sm.add_constant(X)

        # Fit the linear regression model
        try:
            model = sm.OLS(y, X).fit()
            # Capture the summary as a string and write to file
            f.write(f"回归分析结果 - 孕妇代码: {patient_code}\n")
            f.write(model.summary().as_text())
            f.write("\n" + "-" * 50 + "\n")
        except Exception as e:
            f.write(f"对孕妇 {patient_code} 的回归分析失败: {e}\n")
            f.write("-" * 50 + "\n")

print("3D散点图已保存为 '3D_Y_concentration_plot.png'")
print("单体纵向回归分析已完成。回归结果已保存到 'regression_results.txt' 文件中。")