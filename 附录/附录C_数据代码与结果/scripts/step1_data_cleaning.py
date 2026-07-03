import os
import pandas as pd
import glob

base_dir = r"c:\Users\86138\Desktop\LLM代理决策风险偏好实验作业\main experiment results"
output_dir = r"c:\Users\86138\Desktop\LLM代理决策风险偏好实验作业\分析"
os.makedirs(output_dir, exist_ok=True)

print("Finding all_trials_*.csv files...")
all_trials_files = glob.glob(os.path.join(base_dir, '**', 'all_trials_*.csv'), recursive=True)
print(f"Found {len(all_trials_files)} files.")

df_list = []
for f in all_trials_files:
    if 'combined_visualizations' in f:
        continue # skip combined to avoid duplicates
    if 'deepseek' in f and 'flash' not in f and 'pro' not in f:
        continue # skip the root deepseek file to avoid duplicates
    print(f"Reading {f}...")
    try:
        df_list.append(pd.read_csv(f, encoding='utf-8'))
    except UnicodeDecodeError:
        df_list.append(pd.read_csv(f, encoding='gbk'))

df = pd.concat(df_list, ignore_index=True)

print("\n--- 1.1 Data Integrity Check ---")
print(f"Total rows: {len(df)}")
counts = df.groupby(['model', 'thinking', 'condition']).size()
print("\nRows per condition:")
print(counts)
parse_errors = df['parse_error'].sum()
print(f"\nTotal Parse Errors: {parse_errors}")

print("\n--- 1.2 Inconsistent Answers Check ---")
def count_switches(choices_str):
    if pd.isna(choices_str): return 0
    choices = choices_str.split(',')
    switches = 0
    for i in range(1, len(choices)):
        if choices[i] != choices[i-1]:
            switches += 1
    return switches

df['n_switches'] = df['choices'].apply(count_switches)
df['is_valid'] = df['n_switches'] <= 3

invalid_count = (~df['is_valid']).sum()
print(f"Invalid samples (switches > 3): {invalid_count} ({(invalid_count/len(df)*100):.2f}%)")

df_clean = df[df['is_valid']].copy()

print("\n--- 1.3 Add Derived Variables ---")
def get_role(cond):
    if 'self' in cond: return 'self'
    return 'agent'

def get_accountability(cond):
    if 'self' in cond: return 'none'
    if 'invisible' in cond: return 'invisible'
    if 'visible' in cond: return 'visible'
    return 'none'

def get_domain(cond):
    if 'gain' in cond: return 'gain'
    if 'loss' in cond: return 'loss'
    return 'unknown'

df_clean['role_derived'] = df_clean['condition'].apply(get_role)
df_clean['acc_derived'] = df_clean['condition'].apply(get_accountability)
df_clean['domain_derived'] = df_clean['condition'].apply(get_domain)

# Also standardize model names
model_map = {
    'deepseek-v4-flash': 'DeepSeek-Flash',
    'deepseek-v4-pro': 'DeepSeek-Pro',
    'grok:grok-4': 'Grok-4',
    'kimi:kimi-k2-250905': 'Kimi-k2',
    'openai:gpt-4.1': 'GPT-4.1'
}
df_clean['model'] = df_clean['model'].replace(model_map)

out_file = os.path.join(output_dir, 'cleaned_data.csv')
df_clean.to_csv(out_file, index=False)
print(f"\nClean data saved to {out_file}")

with open(os.path.join(output_dir, 'step1_report.txt'), 'w', encoding='utf-8') as f:
    f.write("第一阶段：数据清洗与预处理结果\n")
    f.write(f"总原始样本数: {len(df)}\n")
    f.write(f"JSON解析错误数: {parse_errors}\n")
    f.write(f"不一致切换(>3次)剔除数: {invalid_count} ({(invalid_count/len(df)*100):.2f}%)\n")
    f.write(f"最终有效分析样本数: {len(df_clean)}\n")
