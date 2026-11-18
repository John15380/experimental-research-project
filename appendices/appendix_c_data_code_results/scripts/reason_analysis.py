import pandas as pd
import glob
import json
import os

from project_paths import DATA, RAW_MAIN, RAW_SINGLE

def extract_reasons_from_df(df, is_batch=True):
    records = []
    for _, row in df.iterrows():
        model = row.get('model', 'Unknown')
        condition = row.get('condition', 'Unknown')
        
        if is_batch:
            try:
                reasons = json.loads(row['reasons'])
                for r in reasons:
                    records.append({'model': model, 'condition': condition, 'mode': 'batch', 'text': str(r)})
            except:
                pass
        else:
            reason = str(row.get('reason', ''))
            records.append({'model': model, 'condition': condition, 'mode': 'single', 'text': reason})
    return records

# 1. Load Data
all_records = []

# Main experiment (batch)
batch_files = sorted(RAW_MAIN.rglob('all_trials_*.csv'))
for f in batch_files:
    # exclude think enabled if we want to stick to disabled (as report says)
    try:
        df = pd.read_csv(f, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(f, encoding='gbk')
    if 'thinking' in df.columns:
        df = df[df['thinking'] != 'enabled']
    all_records.extend(extract_reasons_from_df(df, is_batch=True))

# Result2 (single)
# New filenames
single_files = sorted(RAW_SINGLE.rglob('single_trials_*.csv'))
for f in single_files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        all_records.extend(extract_reasons_from_df(df, is_batch=False))

df_texts = pd.DataFrame(all_records)

# 2. Define Keywords
keywords_math = ["期望", "计算", "概率", "算", "大于", "等于", "数学", "乘以", "EV", "价值", "回报"]
keywords_client = ["委托人", "客户", "交代", "解释", "责怪", "免责", "担责", "承担", "不满", "情绪", "受托", "责任", "代理", "负责", "追责"]
keywords_risk = ["风险", "安全", "稳妥", "保守", "避险", "厌恶", "求稳", "保障", "确定", "方差", "损失"]
keywords_adv = ["博", "刺激", "冒险", "激进", "直觉", "潜在"]

def check_keywords(text, kw_list):
    text = str(text).lower()
    for kw in kw_list:
        if kw.lower() in text:
            return 1
    return 0

df_texts['kw_math'] = df_texts['text'].apply(lambda x: check_keywords(x, keywords_math))
df_texts['kw_client'] = df_texts['text'].apply(lambda x: check_keywords(x, keywords_client))
df_texts['kw_risk'] = df_texts['text'].apply(lambda x: check_keywords(x, keywords_risk))
df_texts['kw_adv'] = df_texts['text'].apply(lambda x: check_keywords(x, keywords_adv))

# 3. Aggregate
# We want to see how frequency changes from self to agent_invisible to agent_visible.
# Group by model, mode, condition
df_agg = df_texts.groupby(['model', 'mode', 'condition'])[['kw_math', 'kw_client', 'kw_risk', 'kw_adv']].mean().reset_index()

# Save
out_path = DATA / 'reason_keywords_stats.csv'
df_agg.to_csv(out_path, index=False)
print(f"Stats saved to {out_path}")

# Print overall averages by condition to see if there's a trend
print("\n=== Overall Trend by Condition ===")
trend = df_texts.groupby('condition')[['kw_math', 'kw_client', 'kw_risk']].mean()
print(trend)
