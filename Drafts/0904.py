import pandas as pd

df = pd.read_excel("C:\Users\MX\Downloads\C_attatchment_v2.xlsx", sheet_name = 'male', header=0)

def calculate_days(preg_week_str):
    if pd.isna(preg_week_str):
        return None
    try:
        parts = preg_week_str.split('w+')
        weeks = int(parts[0])
        days = int(parts[1])
        return 7 * weeks + days
    except (ValueError, IndexError):
        return None
    
def calculate_decimal_weeks(preg_week_str):
    if pd.isna(preg_week_str):
        return None
    try:
        parts = preg_week_str.split('w+')
        weeks = int(parts[0])
        days = int(parts[1])
        return round(weeks + days / 7, 4)
    except (ValueError, IndexError):
        return None
    
df['检测孕期（天）'] = df['检测孕周'].apply(calculate_days)
df['检测孕周小数（周）'] = df['检测孕周'].apply(calculate_decimal_weeks)

print(df.head())

df.to_excel("C:\Users\MX\Downloads\C_attatchment_v2_1.xlsx", index=False)