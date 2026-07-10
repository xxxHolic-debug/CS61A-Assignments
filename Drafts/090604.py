# mixed effects regression py

import pandas as pd
import researchpy as rp
import statsmodels.api as sm
import scipy.stats as stats
import chardet
import statsmodels.formula.api as smf

with open(r"C:\Users\MX\Downloads\C_attatchment_v3.csv", 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

df = pd.read_csv(r"C:\Users\MX\Downloads\C_attatchment_v3.csv", encoding=encoding, sep="\t")

df.info()

rp.codebook(df)

rp.summary_cont(df.groupby(["孕妇BMI", "检测孕周小数（周）"])["Y染色体浓度"])

# 固定效应：BMI + 孕周
# 随机效应：孕妇ID（截距随机）
model = smf.mixedlm(
    "Y染色体浓度 ~ 孕妇BMI + 检测孕周小数（周）",
    data=df,
    groups=df["孕妇ID"]
)
result = model.fit()
print(result.summary())