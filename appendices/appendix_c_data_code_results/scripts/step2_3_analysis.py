import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from project_paths import DATA, FIGURES

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] # Chinese font
plt.rcParams['axes.unicode_minus'] = False

data_path = DATA / "cleaned_data.csv"
out_dir = DATA
df = pd.read_csv(data_path)

print("Starting Phase 2 & 3...")
df_main = df[df['thinking'] == 'disabled'].copy()

print("2.1 Descriptive Stats...")
desc_stats = df_main.groupby(['model', 'condition'])['n_safe'].agg(
    n='count', mean='mean', std='std', median='median', min='min', max='max'
).reset_index()
desc_stats.to_csv(os.path.join(out_dir, 'table2_descriptive_stats.csv'), index=False)

print("2.2 Plot A...")
plt.figure(figsize=(14, 7))
sns.barplot(data=df_main, x='model', y='n_safe', hue='condition')
plt.axhline(y=4, color='r', linestyle='--', label='Risk Neutral (EV=4)')
plt.title('图 A：不同模型在各实验条件下的平均安全选择数 ($N_{safe}$)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIGURES / 'Plot_A_mean_comparison.png', dpi=300)
plt.close()

print("2.5 Plot D...")
df_ds = df[df['model'].str.contains('DeepSeek')].copy()
plt.figure(figsize=(12, 6))
sns.barplot(data=df_ds, x='model', y='n_safe', hue='thinking')
plt.axhline(y=4, color='r', linestyle='--', label='Risk Neutral (EV=4)')
plt.title('图 D：DeepSeek开启与关闭深度思考时的风险偏好差异')
plt.tight_layout()
plt.savefig(FIGURES / 'Plot_D_deepseek_thinking.png', dpi=300)
plt.close()

print("2.6 Plot E...")
df_gpt = df_main[df_main['model'] == 'GPT-4.1'].copy()
plt.figure(figsize=(8, 6))
sns.pointplot(data=df_gpt, x='domain_derived', y='n_safe', hue='acc_derived', 
              order=['gain', 'loss'], hue_order=['none', 'invisible', 'visible'])
plt.axhline(y=4, color='r', linestyle='--', alpha=0.5)
plt.title('图 E：损益域与问责性的交互作用 (GPT-4.1)')
plt.tight_layout()
plt.savefig(FIGURES / 'Plot_E_interaction_gpt4.1.png', dpi=300)
plt.close()

print("Running Statistical Tests...")
report_lines = []
report_lines.append("# 第三阶段：统计检验结果报告\n")

report_lines.append("## 3.1 主效应检验 (H1A & H1B: Self vs Agent)")
for m in df_main['model'].unique():
    d_m = df_main[df_main['model'] == m]
    self_vals = d_m[d_m['role_derived'] == 'self']['n_safe']
    agent_vals = d_m[d_m['role_derived'] == 'agent']['n_safe']
    # if all values are identical (like Grok), mannwhitneyu will fail or warn, so we check std
    if self_vals.std() == 0 and agent_vals.std() == 0 and self_vals.mean() == agent_vals.mean():
        report_lines.append(f"Model {m}: Self mean={self_vals.mean():.2f}, Agent mean={agent_vals.mean():.2f} | Identical distributions (p=1.0)")
    else:
        stat, p = stats.mannwhitneyu(self_vals, agent_vals, alternative='two-sided')
        report_lines.append(f"Model {m}: Self mean={self_vals.mean():.2f}, Agent mean={agent_vals.mean():.2f} | Mann-Whitney U={stat}, p={p:.4e}")

report_lines.append("\n## 3.2 损益域框架效应 (Gain vs Loss)")
for m in df_main['model'].unique():
    d_m = df_main[df_main['model'] == m]
    gain_vals = d_m[d_m['domain_derived'] == 'gain']['n_safe']
    loss_vals = d_m[d_m['domain_derived'] == 'loss']['n_safe']
    if gain_vals.std() == 0 and loss_vals.std() == 0 and gain_vals.mean() == loss_vals.mean():
        report_lines.append(f"Model {m}: Gain mean={gain_vals.mean():.2f}, Loss mean={loss_vals.mean():.2f} | Identical distributions (p=1.0)")
    else:
        stat, p = stats.mannwhitneyu(gain_vals, loss_vals, alternative='two-sided')
        report_lines.append(f"Model {m}: Gain mean={gain_vals.mean():.2f}, Loss mean={loss_vals.mean():.2f} | Mann-Whitney U={stat}, p={p:.4e}")

report_lines.append("\n## 3.3 问责性效应 (H2: None vs Invisible vs Visible)")
for m in df_main['model'].unique():
    d_m = df_main[df_main['model'] == m]
    v_none = d_m[d_m['acc_derived'] == 'none']['n_safe']
    v_inv = d_m[d_m['acc_derived'] == 'invisible']['n_safe']
    v_vis = d_m[d_m['acc_derived'] == 'visible']['n_safe']
    if v_none.std() == 0 and v_inv.std() == 0 and v_vis.std() == 0 and v_none.mean() == v_inv.mean():
        report_lines.append(f"Model {m}: Kruskal-Wallis H=0.00, p=1.0000 (Means: None={v_none.mean():.2f}, Inv={v_inv.mean():.2f}, Vis={v_vis.mean():.2f})")
    else:
        stat, p = stats.kruskal(v_none, v_inv, v_vis)
        report_lines.append(f"Model {m}: Kruskal-Wallis H={stat:.2f}, p={p:.4e} (Means: None={v_none.mean():.2f}, Inv={v_inv.mean():.2f}, Vis={v_vis.mean():.2f})")

report_lines.append("\n## 3.4 模型异质性检验 (H3)")
models_data = [df_main[df_main['model'] == m]['n_safe'] for m in df_main['model'].unique()]
stat, p = stats.kruskal(*models_data)
report_lines.append(f"Kruskal-Wallis across all default models: H={stat:.2f}, p={p:.4e}")

report_lines.append("\n## 3.5 双系统专项检验 (DeepSeek Thinking enabled vs disabled)")
for ds in ['DeepSeek-Flash', 'DeepSeek-Pro']:
    d_m = df[df['model'] == ds]
    en_vals = d_m[d_m['thinking'] == 'enabled']['n_safe']
    dis_vals = d_m[d_m['thinking'] == 'disabled']['n_safe']
    if en_vals.std() == 0 and dis_vals.std() == 0 and en_vals.mean() == dis_vals.mean():
        report_lines.append(f"{ds}: Enabled mean={en_vals.mean():.2f}, Disabled mean={dis_vals.mean():.2f} | Identical distributions (p=1.0)")
    else:
        stat, p = stats.mannwhitneyu(en_vals, dis_vals, alternative='two-sided')
        report_lines.append(f"{ds}: Enabled mean={en_vals.mean():.2f}, Disabled mean={dis_vals.mean():.2f} | Mann-Whitney U={stat}, p={p:.4e}")

report_lines.append("\n## 3.8 思维链 (CoT) 文本挖掘 (GPT-4.1 and DeepSeek in Loss domain)")
for m in ['GPT-4.1', 'DeepSeek-Pro']:
    report_lines.append(f"### {m} in Loss domain:")
    df_loss = df_main[(df_main['model'] == m) & (df_main['domain_derived'] == 'loss')].copy()
    for cond in ['loss_self', 'loss_agent_invisible', 'loss_agent_visible']:
        cond_df = df_loss[df_loss['condition'] == cond]
        if 'reasoning_content' in cond_df.columns:
            # Handle potential NaN
            cond_df['reasoning_content'] = cond_df['reasoning_content'].fillna('')
            hegui = cond_df['reasoning_content'].str.contains('合规|风险承受|稳妥|保守|责任|客户', na=False).sum()
            qiwang = cond_df['reasoning_content'].str.contains('期望|概率|数学', na=False).sum()
            report_lines.append(f"- {cond}: mentioned Risk/Responsibility {hegui}/{len(cond_df)} times, mentioned Math/EV {qiwang}/{len(cond_df)} times.")

with open(os.path.join(out_dir, 'statistical_test_results.md'), 'w', encoding='utf-8') as f:
    f.writelines('\n'.join(report_lines))

print("Step 2 and 3 completed successfully!")
