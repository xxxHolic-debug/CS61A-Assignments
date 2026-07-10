import pandas as pd
import re
import os

def split_university_data(input_file, output_file):
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        # 读取Excel文件，尝试不同的引擎
        try:
            df = pd.read_excel(input_file, engine='openpyxl')
        except Exception:
            df = pd.read_excel(input_file, engine='xlrd')
        
        # 假设数据在第一列，如果不是，请修改列名
        data_column = df.columns[0]
        
        # 创建新列存储拆分后的数据
        df['学期'] = ''
        df['国家'] = ''
        df['大学名称'] = ''
        
        # 定义国家列表，按长度排序以避免短名称匹配长名称（如"中国"和"中国台湾"）
        countries = [
            '奥地利', '巴西', '丹麦', '德国', '俄罗斯', '法国', '芬兰', 
            '韩国', '荷兰', '加拿大', '美国', '英国', '日本',
            '意大利', '西班牙', '澳大利亚', '新加坡', '瑞士', '瑞典'
        ]
        # 按国家名称长度降序排序，确保长名称先被匹配
        countries_sorted = sorted(countries, key=lambda x: len(x), reverse=True)
        country_pattern = '|'.join(countries_sorted)
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                text = str(row[data_column]).strip()  # 去除首尾空格
                
                # 提取学期（如"2025秋"）
                semester_match = re.match(r'^\d{4}[春秋夏冬]', text)
                if semester_match:
                    semester = semester_match.group()
                    remaining_text = text[len(semester):].strip()
                    
                    # 提取国家
                    country_match = re.match(f'^({country_pattern})', remaining_text)
                    if country_match:
                        country = country_match.group()
                        university = remaining_text[len(country):].strip()
                        
                        # 保存拆分结果
                        df.at[index, '学期'] = semester
                        df.at[index, '国家'] = country
                        df.at[index, '大学名称'] = university
                    else:
                        # 如果未识别到国家，将剩余文本全部视为大学名称
                        df.at[index, '学期'] = semester
                        df.at[index, '大学名称'] = remaining_text
                else:
                    # 如果未识别到学期，将整个文本视为大学名称
                    df.at[index, '大学名称'] = text
            except Exception as e:
                print(f"处理第{index+1}行时出错: {str(e)}")
                df.at[index, '大学名称'] = text  # 出错时保留原始文本
        
        # 删除原始列
        df = df.drop(columns=[data_column])
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存处理后的结果到新的Excel文件
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"处理完成，结果已保存到 {output_file}")
        return True
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

# 使用示例
if __name__ == "__main__":
    # 输入文件路径
    input_excel = r"C:\Users\MX\Desktop\1.xlsx"
    # 输出文件路径
    output_excel = r"C:\Users\MX\Desktop\1output.xlsx"
    
    # 调用函数处理数据
    split_university_data(input_excel, output_excel)
    