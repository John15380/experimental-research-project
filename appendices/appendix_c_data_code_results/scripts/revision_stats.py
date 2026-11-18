import csv
import random
from collections import defaultdict

from project_paths import DATA as DATA_DIR, ROOT


DATA = DATA_DIR / "cleaned_data.csv"

MODEL_ORDER = [
    "DeepSeek-Flash",
    "DeepSeek-Pro",
    "Grok-4",
    "Kimi-k2",
    "GPT-4.1",
]

DISPLAY = {
    "DeepSeek-Flash": "DeepSeek-V4-Flash",
    "DeepSeek-Pro": "DeepSeek-V4-Pro",
    "Grok-4": "Grok-4",
    "Kimi-k2": "Kimi-k2",
    "GPT-4.1": "GPT-4.1",
}


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def fmt_p(p):
    if p < 0.001:
        return "$<0.001$"
    return f"{p:.3f}"


def fmt_q(q):
    if q < 0.001:
        return "\\textbf{$<0.001$}"
    if q < 0.05:
        return f"\\textbf{{{q:.3f}}}"
    return f"{q:.3f}"


def fmt_delta(x):
    return f"{x:+.2f}"


def bh_adjust(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank, idx in reversed(list(enumerate(order, start=1))):
        prev = min(prev, ps[idx] * m / rank)
        q[idx] = min(prev, 1.0)
    return q


def perm_p_two_group(a, b, *, iters=20000, seed=20260702):
    observed = mean(b) - mean(a)
    if all(x == a[0] for x in a + b):
        return observed, 1.0
    rng = random.Random(seed)
    pooled = list(a) + list(b)
    n_a = len(a)
    extreme = 0
    for _ in range(iters):
        rng.shuffle(pooled)
        diff = mean(pooled[n_a:]) - mean(pooled[:n_a])
        if abs(diff) >= abs(observed) - 1e-12:
            extreme += 1
    return observed, (extreme + 1) / (iters + 1)


def did_value(cells):
    gain = mean(cells[("gain", "visible")]) - mean(cells[("gain", "invisible")])
    loss = mean(cells[("loss", "visible")]) - mean(cells[("loss", "invisible")])
    return gain, loss, loss - gain


def perm_p_did(cells, *, iters=20000, seed=20260703):
    gain, loss, observed = did_value(cells)
    pooled = []
    sizes = []
    keys = [("gain", "invisible"), ("gain", "visible"), ("loss", "invisible"), ("loss", "visible")]
    for key in keys:
        vals = list(cells[key])
        pooled.extend(vals)
        sizes.append(len(vals))
    if all(x == pooled[0] for x in pooled):
        return gain, loss, observed, 1.0
    rng = random.Random(seed)
    extreme = 0
    for _ in range(iters):
        rng.shuffle(pooled)
        start = 0
        draw = {}
        for key, size in zip(keys, sizes):
            draw[key] = pooled[start : start + size]
            start += size
        _, _, stat = did_value(draw)
        if abs(stat) >= abs(observed) - 1e-12:
            extreme += 1
    return gain, loss, observed, (extreme + 1) / (iters + 1)


def load_rows():
    with open(DATA, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["n_safe"] = int(float(row["n_safe"]))
    return rows


def values(rows, model, domain=None, acc=None, role=None):
    out = []
    for row in rows:
        if row["thinking"] != "disabled":
            continue
        if row["model"] != model:
            continue
        if domain is not None and row["domain_derived"] != domain:
            continue
        if acc is not None and row["acc_derived"] != acc:
            continue
        if role is not None and row["role_derived"] != role:
            continue
        out.append(row["n_safe"])
    return out


def write_gain_table(rows):
    stats = []
    for i, model in enumerate(MODEL_ORDER):
        self_vals = values(rows, model, domain="gain", acc="none")
        inv_vals = values(rows, model, domain="gain", acc="invisible")
        vis_vals = values(rows, model, domain="gain", acc="visible")
        d_inv, p_inv = perm_p_two_group(self_vals, inv_vals, seed=20260702 + i)
        d_vis, p_vis = perm_p_two_group(self_vals, vis_vals, seed=20260712 + i)
        stats.append((model, self_vals, inv_vals, vis_vals, d_inv, p_inv, d_vis, p_vis))
    qs = bh_adjust([item[5] for item in stats] + [item[7] for item in stats])
    q_inv = qs[: len(stats)]
    q_vis = qs[len(stats) :]
    lines = [
        "\\begin{table*}[tb]",
        "  \\caption{收益域代理角色效应检验（置换检验，双侧；各条件$n=50$）}",
        "  \\label{tab:gain_agent_effect}",
        "  \\centering",
        "  \\scriptsize",
        "  \\setlength{\\tabcolsep}{3.2pt}",
        "  \\begin{tabular}{lrrrrrrrrr}",
        "    \\toprule",
        "    模型 & Self均值 & Inv均值 & Vis均值 & $\\Delta_{Inv-Self}$ & $p$ & $q_{BH}$ & $\\Delta_{Vis-Self}$ & $p$ & $q_{BH}$ \\\\",
        "    \\midrule",
    ]
    md = ["## 收益域内H1检验（置换检验，双侧）", ""]
    for i, (model, self_vals, inv_vals, vis_vals, d_inv, p_inv, d_vis, p_vis) in enumerate(stats):
        lines.append(
            f"    {DISPLAY[model]} & {mean(self_vals):.2f} & {mean(inv_vals):.2f} & {mean(vis_vals):.2f} & "
            f"{fmt_delta(d_inv)} & {fmt_p(p_inv)} & {fmt_q(q_inv[i])} & {fmt_delta(d_vis)} & {fmt_p(p_vis)} & {fmt_q(q_vis[i])} \\\\"
        )
        md.append(
            f"- {DISPLAY[model]}: Self={mean(self_vals):.2f}, Inv={mean(inv_vals):.2f} "
            f"(Delta={d_inv:+.2f}, p={p_inv:.4f}, q_BH={q_inv[i]:.4f}), Vis={mean(vis_vals):.2f} "
            f"(Delta={d_vis:+.2f}, p={p_vis:.4f}, q_BH={q_vis[i]:.4f})"
        )
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "  \\vspace{0.25em}",
        "",
        "  \\parbox{0.96\\textwidth}{\\footnotesize 注：$\\Delta>0$表示相对于Self条件更谨慎，$\\Delta<0$表示更冒险。置换检验以$N_{\\text{safe}}$均值差为统计量，迭代20,000次，随机种子固定；$q_{BH}$为本表10个成对检验的Benjamini-Hochberg校正值。}",
        "\\end{table*}",
    ]
    with open(ROOT / "paper/tables/table_gain_agent_effect.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return md


def write_interaction_table(rows):
    stats = []
    for i, model in enumerate(MODEL_ORDER):
        cells = defaultdict(list)
        for domain in ["gain", "loss"]:
            for acc in ["invisible", "visible"]:
                cells[(domain, acc)] = values(rows, model, domain=domain, acc=acc)
        stats.append((model, *perm_p_did(cells, seed=20260703 + i)))
    qs = bh_adjust([item[4] for item in stats])
    lines = [
        "\\begin{table}[tb]",
        "  \\caption{问责可见性与损益域的差中差检验（Agent条件内置换检验）}",
        "  \\label{tab:domain_accountability_interaction}",
        "  \\centering",
        "  \\scriptsize",
        "  \\setlength{\\tabcolsep}{3.5pt}",
        "  \\begin{tabular}{lrrrrr}",
        "    \\toprule",
        "    模型 & $\\Delta^{Gain}_{Vis-Inv}$ & $\\Delta^{Loss}_{Vis-Inv}$ & DiD & $p$ & $q_{BH}$ \\\\",
        "    \\midrule",
    ]
    md = ["", "## H2差中差检验（Agent条件内；置换检验，双侧）", ""]
    for i, (model, gain, loss, did, p) in enumerate(stats):
        lines.append(
            f"    {DISPLAY[model]} & {fmt_delta(gain)} & {fmt_delta(loss)} & {fmt_delta(did)} & {fmt_p(p)} & {fmt_q(qs[i])} \\\\"
        )
        md.append(
            f"- {DISPLAY[model]}: Gain Vis-Inv={gain:+.2f}, Loss Vis-Inv={loss:+.2f}, "
            f"DiD={did:+.2f}, p={p:.4f}, q_BH={qs[i]:.4f}"
        )
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "  \\vspace{0.25em}",
        "",
        "  \\parbox{0.96\\linewidth}{\\footnotesize 注：DiD=$\\Delta^{Loss}_{Vis-Inv}-\\Delta^{Gain}_{Vis-Inv}$。正值表示可见性带来的谨慎化在损失域更强。检验仅使用Agent-Invisible与Agent-Visible条件，置换检验迭代20,000次；$q_{BH}$为本表5个模型检验的Benjamini-Hochberg校正值。}",
        "\\end{table}",
    ]
    with open(ROOT / "paper/tables/table_domain_accountability_interaction.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return md


def write_report(md_lines):
    with open(DATA_DIR / "revision_statistical_tests.md", "w", encoding="utf-8") as f:
        f.write("# 修订补充统计检验结果\n\n")
        f.write("本文件为报告修订后新增的最终补充检验，优先级高于早期探索性统计摘要。\n\n")
        f.write("\n".join(md_lines))
        f.write("\n\n正文与表格以 Benjamini-Hochberg 校正后的 q_BH 作为多重比较后的显著性判断依据。")
        f.write("\n")


def main():
    rows = load_rows()
    md = []
    md.extend(write_gain_table(rows))
    md.extend(write_interaction_table(rows))
    write_report(md)


if __name__ == "__main__":
    main()
