# 在male sheet（已删除Y染色体浓度小于4%的数据）的最后两列加上week的计算与day的计算

import pandas as pd


df = pd.read_excel(r"C:\Users\MX\Downloads\C_attatchment_v2.xlsx", header=0)

# 定义处理函数
def calculate_days(preg_week_str):
    """根据“xw+y”或“xw”格式计算总天数"""
    if pd.isna(preg_week_str):
        return None
    try:
        s = str(preg_week_str)
        # 检查是否包含“+”
        if '+' in s:
            parts = s.split('w+')
            weeks = int(parts[0])
            days = int(parts[1])
        else:
            # 如果是“xw”格式，则天数为0
            weeks = int(s.replace('w', ''))
            days = 0
        return 7 * weeks + days
    except (ValueError, IndexError):
        return None

def calculate_decimal_weeks(preg_week_str):
    """根据“xw+y”或“xw”格式计算孕周小数（精确到4位）"""
    if pd.isna(preg_week_str):
        return None
    try:
        s = str(preg_week_str)
        if '+' in s:
            parts = s.split('w+')
            weeks = int(parts[0])
            days = int(parts[1])
        else:
            weeks = int(s.replace('w', ''))
            days = 0
        return round(weeks + days / 7, 4)
    except (ValueError, IndexError):
        return None

# ---

# 3. 应用函数到DataFrame，创建新列
df['检测孕期（天）'] = df['检测孕周'].apply(calculate_days)
df['检测孕周小数（周）'] = df['检测孕周'].apply(calculate_decimal_weeks)

# ---

# 4. 查看结果
print("\n处理后的数据（前5行）：")
print(df.head())

# 如果想把处理好的数据保存到新的Excel文件里
df.to_excel(r"C:\Users\MX\Downloads\C_attatchment_v3.xlsx", index=False)