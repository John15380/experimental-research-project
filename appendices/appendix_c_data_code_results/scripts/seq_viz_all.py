"""全模型序列效应可视化脚本"""
import csv, os
import numpy as np
from collections import defaultdict
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from project_paths import DATA, FIGURES, RAW_SINGLE

plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ANALYSIS = DATA

def read_single_file(path, model_clean, filter_func):
    with open(path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    safe = defaultdict(int)
    for r in rows:
        if not filter_func(r['model']): continue
        key = (model_clean, r['condition'], r['trial'])
        if r['choice'] == 'A':
            safe[key] += 1
    result = defaultdict(list)
    for (m, c, t), n in safe.items():
        result[(m, c)].append(n)
    return result

model_files = [
    ('DeepSeek-Flash', RAW_SINGLE/'deepseek/single_trials_20260622_093438.csv', lambda m: 'flash' in m),
    ('DeepSeek-Pro',   RAW_SINGLE/'deepseek/single_trials_20260622_093438.csv', lambda m: 'pro' in m and 'flash' not in m),
    ('Grok-4',         RAW_SINGLE/'grok_grok-4/single_trials_20260625_000854.csv', lambda m: 'grok' in m.lower()),
    ('Kimi-k2',        RAW_SINGLE/'kimi_kimi-k2-250905/single_trials_20260624_235909.csv', lambda m: 'kimi' in m.lower()),
    ('GPT-4.1',        RAW_SINGLE/'openai_gpt-4.1/single_trials_20260624_233326.csv', lambda m: 'gpt' in m.lower() or 'openai' in m.lower()),
]

single = {}
for mc, path, filt in model_files:
    d = read_single_file(path, mc, filt)
    for k, v in d.items():
        single[k] = v

with open(os.path.join(ANALYSIS, 'cleaned_data.csv'), 'r', encoding='utf-8') as f:
    batch_rows = list(csv.DictReader(f))

batch = defaultdict(list)
for r in batch_rows:
    if r['thinking'] == 'disabled':
        batch[(r['model'], r['condition'])].append(int(r['n_safe']))

models_order = ['DeepSeek-Flash', 'DeepSeek-Pro', 'Grok-4', 'Kimi-k2', 'GPT-4.1']
model_short = ['DS-Flash', 'DS-Pro', 'Grok-4', 'Kimi-k2', 'GPT-4.1']
conds_order = ['gain_self', 'gain_agent_invisible', 'gain_agent_visible',
               'loss_self', 'loss_agent_invisible', 'loss_agent_visible']
cond_labels = ['G/Self', 'G/Inv', 'G/Vis', 'L/Self', 'L/Inv', 'L/Vis']

# ---- 图 F2: 全模型配对均值对比 ----
fig, axes = plt.subplots(1, 5, figsize=(22, 6), sharey=True)
fig.suptitle('Sequence Effect: Batch vs Single-Row (All Models, thinking=disabled)',
             fontsize=13, fontweight='bold')

for mi, (m, ms) in enumerate(zip(models_order, model_short)):
    ax = axes[mi]
    b_means = [np.mean(batch.get((m,c),[0])) for c in conds_order]
    s_means = [np.mean(single.get((m,c),[0])) for c in conds_order]
    b_se = [np.std(batch.get((m,c),[0]), ddof=1)/np.sqrt(max(len(batch.get((m,c),[0])),1)) for c in conds_order]
    s_se = [np.std(single.get((m,c),[0]), ddof=1)/np.sqrt(max(len(single.get((m,c),[0])),1)) for c in conds_order]

    x = np.arange(len(conds_order))
    w = 0.38
    ax.bar(x - w/2, b_means, w, yerr=b_se, label='Batch (n=50)', color='#4A90D9', alpha=0.85, capsize=3)
    ax.bar(x + w/2, s_means, w, yerr=s_se, label='Single', color='#E8724A', alpha=0.85, capsize=3)
    ax.axhline(4, color='gray', ls='--', alpha=0.4, lw=1)
    ax.set_title(ms, fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels, rotation=35, ha='right', fontsize=8)
    ax.set_ylim(0, 11)
    if mi == 0:
        ax.set_ylabel('Mean N_safe', fontsize=11)
    if mi == 4:
        ax.legend(fontsize=8, loc='upper right')

    # 标注显著性
    for i, c in enumerate(conds_order):
        b = batch.get((m,c),[])
        s = single.get((m,c),[])
        if b and s:
            _, p = stats.mannwhitneyu(b, s, alternative='two-sided')
            sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else ''
            if sig:
                top = max(b_means[i], s_means[i]) + 0.6
                ax.text(i, top, sig, ha='center', fontsize=10, color='red', fontweight='bold')

    # 域分隔线
    ax.axvline(2.5, color='green', ls=':', alpha=0.4, lw=1)

plt.tight_layout()
out_f2 = FIGURES / 'Plot_F2_sequence_all_models.png'
plt.savefig(out_f2, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {out_f2}")

# ---- 图 I: 整体Delta汇总 heatmap ----
fig, ax = plt.subplots(figsize=(11, 5))
delta_matrix = []
for m in models_order:
    row = []
    for c in conds_order:
        b = batch.get((m,c),[])
        s = single.get((m,c),[])
        if b and s:
            row.append(np.mean(s) - np.mean(b))
        else:
            row.append(np.nan)
    delta_matrix.append(row)

dm = np.array(delta_matrix, dtype=float)
im = ax.imshow(dm, cmap='RdYlGn', vmin=-5, vmax=5, aspect='auto')
plt.colorbar(im, ax=ax, label='Delta (Single - Batch)')
ax.set_xticks(range(len(conds_order)))
ax.set_xticklabels(cond_labels, fontsize=11)
ax.set_yticks(range(len(models_order)))
ax.set_yticklabels(model_short, fontsize=11)
ax.set_title('Sequence Effect Delta Matrix\n(Single-Row minus Batch, green=more conservative in single)',
             fontsize=12, fontweight='bold')

for i in range(len(models_order)):
    for j in range(len(conds_order)):
        val = dm[i,j]
        if not np.isnan(val):
            b = batch.get((models_order[i], conds_order[j]),[])
            s = single.get((models_order[i], conds_order[j]),[])
            sig_star = ''
            if b and s:
                _, p = stats.mannwhitneyu(b, s, alternative='two-sided')
                sig_star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else ''
            ax.text(j, i, f'{val:+.1f}\n{sig_star}', ha='center', va='center',
                    fontsize=9, fontweight='bold',
                    color='black' if abs(val) < 3 else 'white')

plt.tight_layout()
out_i = FIGURES / 'Plot_I_sequence_delta_heatmap.png'
plt.savefig(out_i, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {out_i}")

print("All done.")
