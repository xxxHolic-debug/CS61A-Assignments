import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import statsmodels.api as sm
import statsmodels.formula.api as smf

# -- 准备数据和初步筛选 --
file_path = r"C:\Users\MX\Downloads\C_attatchment_v3.xlsx"
df = pd.read_excel(file_path)
print("DataFrame 中的所有列名：")
print(df.columns)



df['孕妇代码'] = df['孕妇代码'].astype(str)

# 找出进行了多次检查的孕妇代码
# 筛选出计数值大于1的孕妇代码，即有多条记录的孕妇
multi_test_pregnant_women = df['孕妇代码'].value_counts()
multi_test_pregnant_women = multi_test_pregnant_women[multi_test_pregnant_women > 1].index.tolist()

# 基于筛选出的孕妇代码，创建新的DataFrame
df_longitudinal = df[df['孕妇代码'].isin(multi_test_pregnant_women)].copy()

print(f"原始数据共有 {len(df)} 行。")
print(f"共有 {len(multi_test_pregnant_women)} 位孕妇进行了多次检查。")
print("筛选后的纵向分析数据集前5行：")
print(df_longitudinal.head())


# -- 单体纵向分析 --

y_concentration_col = 'Y染色体浓度'
decimal_week_col = '检测孕周小数（周）'

# 设置图形风格
sns.set(style="whitegrid")

output_folder = output_folder = r'D:\MX Files\college\career\MM\2025CUMCM_gaojiaoshe\pregnancy_plots_male'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False 

# 遍历每一位多次检查的孕妇
for preg_code in multi_test_pregnant_women:
    # 筛选出当前孕妇的数据
    preg_data = df_longitudinal[df_longitudinal['孕妇代码'] == preg_code].copy()

    # 如果数据点少于2个，无法进行回归，跳过
    if len(preg_data) < 2:
        continue

    # 绘图
    plt.figure(figsize=(8, 6))
    plt.title(f'孕妇 {preg_code} Y染色体浓度随孕周变化')
    plt.xlabel(decimal_week_col)
    plt.ylabel(y_concentration_col)
    
    # 绘制散点图
    sns.scatterplot(data=preg_data, x=decimal_week_col, y=y_concentration_col)

    # 进行线性回归
    try:
        # np.polyfit进行线性拟合，返回斜率和截距
        fit = np.polyfit(preg_data[decimal_week_col], preg_data[y_concentration_col], 1)
        # 生成回归线
        fit_fn = np.poly1d(fit)
        plt.plot(preg_data[decimal_week_col], fit_fn(preg_data[decimal_week_col]), color='red')
        plt.legend(['线性回归', '实际数据'])
    except:
        print(f"无法为孕妇 {preg_code} 进行线性回归。")
    
    file_name = f"{preg_code}_y_concentration_plot.png"
    save_path = os.path.join(output_folder, file_name)
    plt.savefig(save_path)

    plt.close()

print(f"\n所有图形已保存至 '{output_folder}' 文件夹中。")


# -- 回归分析和显著性检验 --
# 注意： 考虑到你的数据量，线性回归可能不足以描述所有情况。你提到的非线性回归，通常需要根据具体情况选择模型。这里仍以线性模型为例。
report_folder = r'D:\MX Files\college\career\MM\2025CUMCM_gaojiaoshe\pregnancy_plots_male'
if not os.path.exists(report_folder):
    os.makedirs(report_folder)

output_file_name = "all_regression_reports.txt"
output_path = os.path.join(report_folder, output_file_name)

# 存储每个孕妇的回归结果
regression_results = []

with open(output_path, 'w', encoding='utf-8') as f:
    
    # 遍历每一位多次检查的孕妇
    for preg_code in multi_test_pregnant_women:
        preg_data = df_longitudinal[df_longitudinal['孕妇代码'] == preg_code].copy()

        if len(preg_data) < 2:
            continue

        X = preg_data[[decimal_week_col, '孕妇BMI']].copy()
        y = preg_data[y_concentration_col]

        # 添加截距项
        X = sm.add_constant(X)

        try:
            model = sm.OLS(y, X).fit()

            # --- 写入报告到文件 ---
            # 写入标题，方便区分每个孕妇的报告
            f.write(f"==== 孕妇 {preg_code} 回归分析报告 ====\n")
            
            # 写入报告内容
            f.write(model.summary().as_text())
            
            # 在每个报告后添加分隔线和空行
            f.write("\n" + "="*80 + "\n\n")

            # 将关键结果保存下来以便后续分析
            regression_results.append({
                '孕妇代码': preg_code,
                'R-squared': model.rsquared,
                '孕周_p_value': model.pvalues[decimal_week_col],
                'BMI_p_value': model.pvalues['孕妇BMI']
            })
        except Exception as e:
            print(f"孕妇 {preg_code} 回归分析失败，原因: {e}")

print(f"\n所有回归报告已写入单个文件：{output_path}")


# -- 群体横向分析 见090602 --