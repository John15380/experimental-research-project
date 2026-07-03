"""全模型序列效应稳健性检验分析脚本"""
import csv, os, sys
import numpy as np
from collections import defaultdict
from scipy import stats

BASE = r"c:\Users\86138\Desktop\LLM代理决策风险偏好实验作业"
ANALYSIS = os.path.join(BASE, "分析")

# ============================================================
# 1. 读取所有 single 数据
# ============================================================
def read_single_file(path, model_clean, filter_func):
    with open(path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    safe = defaultdict(int)
    total = defaultdict(int)
    for r in rows:
        if not filter_func(r['model']): continue
        key = (model_clean, r['condition'], r['trial'])
        total[key] += 1
        if r['choice'] == 'A':
            safe[key] += 1
    # 聚合: N_safe per (model, condition, trial)
    result = defaultdict(list)
    for (m, c, t), n in safe.items():
        result[(m, c)].append(n)
    return result

model_files = [
    ('DeepSeek-Flash', BASE+r'\result2\deepseek\single_trials_20260622_093438.csv', lambda m: 'flash' in m),
    ('DeepSeek-Pro',   BASE+r'\result2\deepseek\single_trials_20260622_093438.csv', lambda m: 'pro' in m and 'flash' not in m),
    ('Grok-4',         BASE+r'\result2\grok_grok-4\single_trials_20260625_000854.csv', lambda m: 'grok' in m.lower()),
    ('Kimi-k2',        BASE+r'\result2\kimi_kimi-k2-250905\single_trials_20260624_235909.csv', lambda m: 'kimi' in m.lower()),
    ('GPT-4.1',        BASE+r'\result2\openai_gpt-4.1\single_trials_20260624_233326.csv', lambda m: 'gpt' in m.lower() or 'openai' in m.lower()),
]

single = {}
for mc, path, filt in model_files:
    d = read_single_file(path, mc, filt)
    for k, v in d.items():
        single[k] = v

# ============================================================
# 2. 读取主实验(batch)数据
# ============================================================
with open(os.path.join(ANALYSIS, 'cleaned_data.csv'), 'r', encoding='utf-8') as f:
    batch_rows = list(csv.DictReader(f))

batch = defaultdict(list)
for r in batch_rows:
    if r['thinking'] == 'disabled':
        batch[(r['model'], r['condition'])].append(int(r['n_safe']))

# ============================================================
# 3. 统计检验 - 全模型
# ============================================================
models_order = ['DeepSeek-Flash', 'DeepSeek-Pro', 'Grok-4', 'Kimi-k2', 'GPT-4.1']
conds_order = ['gain_self', 'gain_agent_invisible', 'gain_agent_visible',
               'loss_self', 'loss_agent_invisible', 'loss_agent_visible']

all_comparisons = []
for m in models_order:
    for c in conds_order:
        b = batch.get((m, c), [])
        s = single.get((m, c), [])
        if not b or not s:
            continue
        b_arr = np.array(b, dtype=float)
        s_arr = np.array(s, dtype=float)
        u, p = stats.mannwhitneyu(b_arr, s_arr, alternative='two-sided')
        r_eff = 1 - 2*u / (len(b_arr)*len(s_arr))
        all_comparisons.append({
            'model': m, 'condition': c,
            'batch_n': len(b), 'batch_mean': np.mean(b_arr), 'batch_sd': np.std(b_arr, ddof=1),
            'single_n': len(s), 'single_mean': np.mean(s_arr), 'single_sd': np.std(s_arr, ddof=1) if len(s)>1 else 0,
            'delta': np.mean(s_arr) - np.mean(b_arr),
            'U': u, 'p': p, 'r_eff': r_eff,
        })

n_tests = len(all_comparisons)
alpha_bonf = 0.05 / n_tests

print(f"共 {n_tests} 个比较，Bonferroni alpha = {alpha_bonf:.4f}")
print()

# ============================================================
# 4. 按模型整体检验
# ============================================================
print("=== 各模型整体序列效应 ===")
model_overall = {}
for m in models_order:
    all_b, all_s = [], []
    for c in conds_order:
        all_b.extend(batch.get((m, c), []))
        all_s.extend(single.get((m, c), []))
    if all_b and all_s:
        u, p = stats.mannwhitneyu(all_b, all_s, alternative='two-sided')
        r_eff = 1 - 2*u/(len(all_b)*len(all_s))
        sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'n.s.'
        model_overall[m] = {'batch_mean': np.mean(all_b), 'single_mean': np.mean(all_s),
                            'delta': np.mean(all_s)-np.mean(all_b), 'U': u, 'p': p, 'r': r_eff, 'sig': sig}
        print(f"{m:20s}: batch={np.mean(all_b):.2f}, single={np.mean(all_s):.2f}, delta={np.mean(all_s)-np.mean(all_b):+.2f}, U={u:.1f}, p={p:.6f} {sig}, r={r_eff:+.3f}")

# ============================================================
# 5. 检验核心假设：条件间相对顺序是否保持
# ============================================================
print()
print("=== 条件间相对排序检验（Spearman相关：batch均值 vs single均值） ===")
for m in models_order:
    b_means = [np.mean(batch.get((m,c),[])) for c in conds_order if batch.get((m,c))]
    s_means = [np.mean(single.get((m,c),[])) for c in conds_order if single.get((m,c))]
    valid_conds = [c for c in conds_order if batch.get((m,c)) and single.get((m,c))]
    if len(valid_conds) >= 3:
        b_m = [np.mean(batch[(m,c)]) for c in valid_conds]
        s_m = [np.mean(single[(m,c)]) for c in valid_conds]
        rho, p_sp = stats.spearmanr(b_m, s_m)
        print(f"{m:20s}: Spearman rho={rho:.3f}, p={p_sp:.4f}")

# ============================================================
# 6. 输出完整结果表
# ============================================================
print()
print("=== 逐条件结果 ===")
print(f"{'Model':20s} | {'Condition':25s} | BatchN | BatchMean | SingleN | SingleMean | Delta | U | p | sig | r | Bonf")
for comp in all_comparisons:
    sig = '***' if comp['p']<0.001 else '**' if comp['p']<0.01 else '*' if comp['p']<0.05 else 'n.s.'
    bonf = 'Y' if comp['p'] < alpha_bonf else 'N'
    print(f"{comp['model']:20s} | {comp['condition']:25s} | {comp['batch_n']:6d} | {comp['batch_mean']:9.2f} | {comp['single_n']:7d} | {comp['single_mean']:10.2f} | {comp['delta']:+5.2f} | {comp['U']:8.1f} | {comp['p']:.5f} | {sig:4s} | {comp['r_eff']:+.3f} | {bonf}")

# Save results
out = os.path.join(ANALYSIS, "sequence_effect_all_models.csv")
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['model','condition','batch_n','batch_mean','batch_sd',
                                       'single_n','single_mean','single_sd','delta','U','p','r_eff'])
    w.writeheader()
    w.writerows(all_comparisons)
print(f"\nSaved: {out}")
